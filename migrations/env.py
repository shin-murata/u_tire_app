import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# app/models.py から SQLAlchemy インスタンスをインポート
from models import db, InputPage  # models.py 内の SQLAlchemy インスタンスとモデルをインポート

# モデルのメタデータを設定
target_metadata = db.metadata  # db.metadata を利用


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_metadata():
    """
    以前使用されていた関数。
    現在は db.metadata を直接使用しているため未使用。
    """
    logger.info(f"Current metadata tables: {list(db.metadata.tables.keys())}")
    return db.metadata



def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    #import pdb; pdb.set_trace()  # デバッグポイントを追加

   # process_revision_directives を先に定義
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')
    
    # conf_args の内容を確認
    conf_args = {
        "process_revision_directives": process_revision_directives,
        "compare_server_default": True,
        "compare_type": True,
    }

    # conf_args の内容を確認
    logger.info(f"conf_args: {conf_args}")

    connectable = get_engine()
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    print(f"Target metadata tables: {get_metadata().tables.keys()}")

    # デバッグ: get_metadata()の内容をログに出力
    logger.info(f"Available metadata tables: {list(get_metadata().tables.keys())}")
    logger.info(f"InputPage table info: {get_metadata().tables.get('input_page')}")

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
   

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args  # ここで conf_args を展開して渡す
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


def include_object(object, name, type_, reflected, compare_to):
    return True
