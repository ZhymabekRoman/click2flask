from flask import request, jsonify, make_response
from unittest.mock import patch
import click
from loguru import logger
from click.types import StringParamType

captured_outputs = {}


def custom_echo(text, *args, **kwargs):
    # Assuming the function name is passed as a keyword argument
    func_name = kwargs.get("func_name", "unknown")
    if func_name not in captured_outputs:
        captured_outputs[func_name] = []
    captured_outputs[func_name].append(str(text))


def register_group(app, group):
    for command_name, command in group.commands.items():
        if isinstance(command, click.Group):
            logger.info(f"Registering subgroup: {command_name}")
            register_group(command)
        else:
            logger.info(f"Registering command in group: {command_name}")
            register_command(app, command)


def register_command(app, command, use_echo_output=False):
    command_name = command.name
    route = f"/api/{command_name}"
    logger.info(f"Creating route for command: {route}")

    @app.route(route, methods=["GET", "POST"], endpoint=f"command_{command_name}")
    def command_route_safe():
        def command_route():
            captured_outputs[command_name] = []
            options = {
                param.name: param
                for param in command.params
                if isinstance(param, click.Option)
            }
            provided_options = {}

            def parse_options(request_data, method):
                for option_name, option in options.items():
                    value = None
                    if method == "GET":
                        value = request_data.get(option_name) or next(
                            (
                                request_data.get(opt.lstrip("-"))
                                for opt in option.opts
                                if request_data.get(opt.lstrip("-"))
                            ),
                            None,
                        )
                    elif method == "POST":
                        value = request_data.get(option_name) or next(
                            (
                                request_data.get(opt.lstrip("-"))
                                for opt in option.opts
                                if request_data.get(opt.lstrip("-"))
                            ),
                            None,
                        )

                    if value is None and option.default is not None:
                        value = option.default

                    if option.is_flag:
                        value = value if isinstance(value, bool) else value is not None
                    elif (
                        isinstance(option.type, click.Choice)
                        and value not in option.type.choices
                    ):
                        error_response = jsonify(
                            {
                                "error": f"Invalid value for --{option_name}. Choose from {option.type.choices}."
                            }
                        )
                        return make_response(error_response, 400)
                    elif isinstance(option.type, StringParamType):
                        value = option.type(value)

                    if option.required and value is None:
                        error_response = jsonify(
                            {"error": f"Missing required option: --{option_name}"}
                        )
                        return make_response(error_response, 400)
                    provided_options[option_name] = value

            if request.method == "GET":
                response = parse_options(request.args, "GET")
                if response:
                    return response
            elif request.method == "POST":
                response = parse_options(request.json or {}, "POST")
                if response:
                    return response

            if use_echo_output:
                with patch("click.echo") as mock_echo:
                    mock_echo.side_effect = lambda text, *args, **kwargs: custom_echo(
                        text, func_name=command_name, *args, **kwargs
                    )
                    command.callback(**provided_options)
                output = "\n".join(captured_outputs[command_name])
                return jsonify({"message": output})
            else:
                result = command.callback(**provided_options)
                if isinstance(result, str):
                    return jsonify({"message": result})
                elif isinstance(result, dict):
                    return jsonify(result)
                else:
                    return jsonify({"error": "Unsupported return type from command"})

        try:
            return command_route()
        except Exception as e:
            return jsonify({"error": f"Exception: {e}"}), 500