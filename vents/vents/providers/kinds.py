from clipped.utils.enums import PEnum


class ProviderKind(str, PEnum):
    HOST_PATH = "host_path"
    VOLUME_CLAIM = "volume_claim"
    GCS = "gcs"
    S3 = "s3"
    WASB = "wasb"
    REGISTRY = "registry"
    GIT = "git"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    MYSQL = "mysql"
    POSTGRES = "postgres"
    ORACLE = "oracle"
    VERTICA = "vertica"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    REDIS = "redis"
    PRESTO = "presto"
    MONGO = "mongo"
    CASSANDRA = "cassandra"
    FTP = "ftp"
    GRPC = "grpc"
    HDFS = "hdfs"
    HTTP = "http"
    PIG_CLI = "pig_cli"
    HIVE_CLI = "hive_cli"
    HIVE_METASTORE = "hive_metastore"
    HIVE_SERVER2 = "hive_server2"
    JDBC = "jdbc"
    JENKINS = "jenkins"
    SAMBA = "samba"
    SNOWFLAKE = "snowflake"
    SSH = "ssh"
    CLOUDANT = "cloudant"
    DATABRICKS = "databricks"
    SEGMENT = "segment"
    SLACK = "slack"
    TEAMS = "teams"
    EMAIL = "email"
    DISCORD = "discord"
    MATTERMOST = "mattermost"
    PAGERDUTY = "pagerduty"
    HIPCHAT = "hipchat"
    WEBHOOK = "webhook"
    CUSTOM = "custom"

    @classmethod
    def mount_values(cls):
        return {cls.HOST_PATH, cls.VOLUME_CLAIM}

    @classmethod
    def blob_values(cls):
        return {cls.GCS, cls.S3, cls.WASB}

    @classmethod
    def artifact_values(cls):
        return cls.blob_values() | cls.mount_values()

    @classmethod
    def host_values(cls):
        return {cls.GIT, cls.REGISTRY}

    @classmethod
    def is_bucket(cls, kind):
        return kind in cls.blob_values()

    @classmethod
    def is_mount(cls, kind):
        return kind in cls.mount_values()

    @classmethod
    def is_host_path(cls, kind):
        return kind == cls.HOST_PATH

    @classmethod
    def is_volume_claim(cls, kind):
        return kind == cls.VOLUME_CLAIM

    @classmethod
    def is_artifact(cls, kind):
        return kind in cls.artifact_values()

    @classmethod
    def is_git(cls, kind):
        return kind == cls.GIT

    @classmethod
    def is_ssh(cls, kind):
        return kind == cls.SSH

    @classmethod
    def is_registry(cls, kind):
        return kind == cls.REGISTRY

    @classmethod
    def is_s3(cls, kind):
        return kind == cls.S3

    @classmethod
    def is_wasb(cls, kind):
        return kind == cls.WASB

    @classmethod
    def is_gcs(cls, kind):
        return kind == cls.GCS
