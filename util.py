def validate_json_structure(request):
    if not request.is_json:
        raise AttributeError("Invalid body, must be a JSON")
    else:
        try:
            request.json
        except Exception:
            raise AttributeError("Invalid body, must be a JSON")
