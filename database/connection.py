import psycopg2


def get_connection():
    return psycopg2.connect(
        host="aws-0-us-west-2.pooler.supabase.com",
        database="postgres",
        user="postgres.fdepgcrcngsgdsvxfjpi",
        password="C,9b4zYMyi6Wa?e",
        port=6543,
        sslmode="require"
    )