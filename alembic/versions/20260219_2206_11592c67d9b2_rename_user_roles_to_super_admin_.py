"""rename_user_roles_to_super_admin_calling_texting_team

Revision ID: 11592c67d9b2
Revises: 6f8f9de11d3d
Create Date: 2026-02-19 22:06:42.125098

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11592c67d9b2'
down_revision = '6f8f9de11d3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Decouple column from the old enum type by casting to plain text
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE TEXT")

    # Step 2: Rename old enum so we can reuse the type name
    op.execute("ALTER TYPE userrole RENAME TO userrole_old")

    # Step 3: Create new enum with the desired values
    op.execute("CREATE TYPE userrole AS ENUM ('super_admin', 'calling_team', 'texting_team')")

    # Step 4: Migrate existing data (DB stored values are uppercase Python enum names)
    op.execute("UPDATE users SET role = 'super_admin' WHERE LOWER(role) = 'admin'")
    op.execute("UPDATE users SET role = 'calling_team' WHERE LOWER(role) = 'user'")

    # Step 5: Re-attach column to the new enum
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")

    # Step 6: Clean up old enum
    op.execute("DROP TYPE userrole_old")


def downgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE TEXT")
    op.execute("ALTER TYPE userrole RENAME TO userrole_old")
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'user')")

    op.execute("UPDATE users SET role = 'admin' WHERE role = 'super_admin'")
    op.execute("UPDATE users SET role = 'user' WHERE role IN ('calling_team', 'texting_team')")

    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")
    op.execute("DROP TYPE userrole_old")
