"""initial schema - all tables

Revision ID: 001
Revises: 
Create Date: 2026-03-29
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=False, server_default='user'),
        sa.Column('is_verified', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Companies table
    op.create_table(
        'companies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('industry', sa.String(100)),
        sa.Column('website', sa.String),
        sa.Column('contact_email', sa.String),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Contacts table
    op.create_table(
        'contacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('role', sa.String(100)),
        sa.Column('linkedin', sa.String),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='SET NULL')),
        sa.Column('status', sa.Enum('draft', 'active', 'processing', 'completed', 'failed', name='campaignstatus'), nullable=False, server_default='draft'),
        sa.Column('type', sa.String(100)),
        sa.Column('goal', sa.Text),
        sa.Column('target_audience', sa.Text),
        sa.Column('budget', sa.Numeric(12, 2)),
        sa.Column('partnership_type', sa.String(100)),
        sa.Column('target_sponsor_profile', JSONB, server_default='{}'),
        sa.Column('offerings', JSONB, server_default='{}'),
        sa.Column('strategy_output', JSONB, server_default='{}'),
        sa.Column('task_id', sa.String),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Outreach table
    op.create_table(
        'outreach',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('contact_id', UUID(as_uuid=True), sa.ForeignKey('contacts.id', ondelete='SET NULL')),
        sa.Column('status', sa.Enum('scheduled', 'sent', 'opened', 'replied', 'failed', name='outreachstatus'), nullable=False, server_default='scheduled'),
        sa.Column('subject', sa.Text),
        sa.Column('body', sa.Text),
        sa.Column('cta', sa.Text),
        sa.Column('eval_score', sa.Float),
        sa.Column('eval_details', JSONB, server_default='{}'),
        sa.Column('follow_up_dates', JSONB, server_default='[]'),
        sa.Column('sent_at', sa.DateTime(timezone=True)),
        sa.Column('opened_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Embeddings table (pgvector)
    op.create_table(
        'embeddings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('vector', Vector(1536), nullable=False),
        sa.Column('metadata_', JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_embeddings_entity_type', 'embeddings', ['entity_type'])

    # HNSW index for vector similarity search
    op.execute('''
        CREATE INDEX embeddings_hnsw_idx ON embeddings
        USING hnsw (vector vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    ''')


def downgrade() -> None:
    op.drop_table('embeddings')
    op.drop_table('outreach')
    op.drop_table('campaigns')
    op.drop_table('contacts')
    op.drop_table('companies')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS campaignstatus')
    op.execute('DROP TYPE IF EXISTS outreachstatus')
