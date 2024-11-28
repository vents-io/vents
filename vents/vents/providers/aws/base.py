from typing import List, Optional, Union

from clipped.utils.bools import to_bool

from vents.settings import VENTS_CONFIG


def get_aws_access_key_id(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AWS_ACCESS_KEY_ID"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_aws_secret_access_key(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AWS_SECRET_ACCESS_KEY"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_aws_security_token(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AWS_SECURITY_TOKEN"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_region(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AWS_REGION"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_endpoint_url(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AWS_ENDPOINT_URL"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_aws_use_ssl(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[bool]:
    keys = keys or ["AWS_USE_SSL"]
    value = VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore
    if value is not None:
        return to_bool(value)
    return True


def get_aws_verify_ssl(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[bool]:
    keys = keys or ["AWS_VERIFY_SSL"]
    value = VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore
    if value is not None:
        return to_bool(value)
    return None


def get_aws_session(
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
):
    import boto3

    aws_access_key_id = get_aws_access_key_id(
        context_paths=context_paths, schema=schema, env=env
    )
    aws_secret_access_key = get_aws_secret_access_key(
        context_paths=context_paths, schema=schema, env=env
    )
    aws_session_token = get_aws_security_token(
        context_paths=context_paths, schema=schema, env=env
    )
    region_name = get_region(context_paths=context_paths, schema=schema, env=env)
    return boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region_name,
    )


def get_aws_client(
    client_type,
    context_paths: Optional[List[str]] = None,
):
    session = get_aws_session(
        context_paths=context_paths,
    )
    endpoint_url = get_endpoint_url(context_paths=context_paths)
    aws_use_ssl = get_aws_use_ssl(context_paths=context_paths)
    aws_verify_ssl = get_aws_verify_ssl(context_paths=context_paths)
    return session.client(
        client_type,
        endpoint_url=endpoint_url,
        use_ssl=aws_use_ssl,
        verify=aws_verify_ssl,
    )


def get_aws_resource(
    resource_type,
    schema: Optional[str] = None,
    env: Optional[str] = None,
    context_paths: Optional[List[str]] = None,
):
    session = get_aws_session(context_paths=context_paths, schema=schema, env=env)
    endpoint_url = get_endpoint_url(context_paths=context_paths)
    aws_use_ssl = get_aws_use_ssl(context_paths=context_paths)
    aws_verify_ssl = get_aws_verify_ssl(context_paths=context_paths)
    return session.resource(
        resource_type,
        endpoint_url=endpoint_url,
        use_ssl=aws_use_ssl,
        verify=aws_verify_ssl,
    )


def get_aws_assume_role(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[bool]:
    keys = keys or ["AWS_ASSUME_ROLE"]
    value = VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore
    if value is not None:
        return to_bool(value)
    return None


def get_aws_role_arn(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AWS_ROLE_ARN"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_aws_session_name(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AWS_SESSION_NAME"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore


def get_aws_session_duration(
    keys: Optional[Union[str, List[str]]] = None,
    context_paths: Optional[List[str]] = None,
    schema: Optional[str] = None,
    env: Optional[str] = None,
) -> Optional[str]:
    keys = keys or ["AWS_SESSION_DURATION"]
    return VENTS_CONFIG.read_keys(
        context_paths=context_paths, schema=schema, env=env, keys=keys
    )  # type: ignore
