#!/usr/bin/env python
import os
import sys
import time
import boto3
from datetime import datetime
from subprocess import run, PIPE
from pathlib import Path

def create_db_backup():
    """Create a database backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_{timestamp}.sql'
    backup_path = Path('/app/backups') / backup_file

    # Create backup directory if it doesn't exist
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    # Create database backup
    result = run([
        'pg_dump',
        '-h', os.environ.get('DB_HOST'),
        '-U', os.environ.get('DB_USER'),
        '-d', os.environ.get('DB_NAME'),
        '-F', 'c',  # Custom format
        '-f', str(backup_path)
    ], env={'PGPASSWORD': os.environ.get('DB_PASSWORD')}, stderr=PIPE)

    if result.returncode != 0:
        raise Exception(f"Database backup failed: {result.stderr.decode()}")

    return backup_path

def upload_to_s3(file_path):
    """Upload backup to S3"""
    s3 = boto3.client('s3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_S3_REGION_NAME')
    )

    bucket = os.environ.get('AWS_BACKUP_BUCKET')
    key = f'backups/{file_path.name}'

    s3.upload_file(str(file_path), bucket, key)
    return f's3://{bucket}/{key}'

def cleanup_old_backups():
    """Remove old backup files"""
    backup_dir = Path('/app/backups')
    backup_count = int(os.environ.get('BACKUP_COUNT', 30))
    
    # List all backup files sorted by modification time
    backup_files = sorted(
        backup_dir.glob('backup_*.sql'),
        key=lambda x: x.stat().st_mtime
    )

    # Remove old backups
    while len(backup_files) > backup_count:
        backup_files[0].unlink()
        backup_files.pop(0)

def main():
    try:
        print("Starting backup process...")
        backup_path = create_db_backup()
        print(f"Database backup created: {backup_path}")

        s3_path = upload_to_s3(backup_path)
        print(f"Backup uploaded to S3: {s3_path}")

        cleanup_old_backups()
        print("Old backups cleaned up")

        print("Backup process completed successfully")
        return 0
    except Exception as e:
        print(f"Backup failed: {str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main()) 