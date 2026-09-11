"""bug fixing

Revision ID: d68cd1697950
Revises: c9b57d421557
Create Date: 2026-03-04 14:52:17.504654
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision: str = 'd68cd1697950'
down_revision: Union[str, Sequence[str], None] = 'c9b57d421557'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---- CREATE ENUM FIRST ----
    message_status_enum = postgresql.ENUM(
        'COMPLETED',
        'STREAMING',
        'ABORTED',
        name='message_status_enum'
    )

    message_status_enum.create(op.get_bind(), checkfirst=True)

    # ---- ADD COLUMNS ----
    op.add_column(
        'chat_histories',
        sa.Column('message_index', sa.Integer(), nullable=True)
    )

    op.add_column(
        'chat_histories',
        sa.Column(
            'status',
            sa.Enum(
                'COMPLETED',
                'STREAMING',
                'ABORTED',
                name='message_status_enum'
            ),
            nullable=False,
            server_default='STREAMING'
        )
    )

    op.add_column(
        'chat_histories',
        sa.Column('model_name', sa.String(), nullable=True)
    )

    op.add_column(
        'chat_histories',
        sa.Column('provider_name', sa.String(), nullable=True)
    )

    op.add_column(
        'chat_histories',
        sa.Column('input_tokens', sa.Integer(), nullable=False, server_default='0')
    )

    op.add_column(
        'chat_histories',
        sa.Column('output_tokens', sa.Integer(), nullable=False, server_default='0')
    )

    op.add_column(
        'chat_histories',
        sa.Column('latency_ms', sa.Integer(), nullable=False, server_default='0')
    )

    op.add_column(
        'chat_histories',
        sa.Column('message_metadata', sa.JSON(), nullable=True)
    )

    # ---- ALTER COLUMN ----
    op.alter_column(
        'chat_histories',
        'user_id',
        existing_type=sa.UUID(),
        nullable=True
    )

    # ---- INDEX ----
    op.create_index(
        op.f('ix_chat_histories_message_index'),
        'chat_histories',
        ['message_index'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f('ix_chat_histories_message_index'), table_name='chat_histories')

    op.alter_column(
        'chat_histories',
        'user_id',
        existing_type=sa.UUID(),
        nullable=False
    )

    op.drop_column('chat_histories', 'message_metadata')
    op.drop_column('chat_histories', 'latency_ms')
    op.drop_column('chat_histories', 'output_tokens')
    op.drop_column('chat_histories', 'input_tokens')
    op.drop_column('chat_histories', 'provider_name')
    op.drop_column('chat_histories', 'model_name')
    op.drop_column('chat_histories', 'status')
    op.drop_column('chat_histories', 'message_index')

    # ---- DROP ENUM ----
    message_status_enum = postgresql.ENUM(
        'COMPLETED',
        'STREAMING',
        'ABORTED',
        name='message_status_enum'
    )

    message_status_enum.drop(op.get_bind(), checkfirst=True)