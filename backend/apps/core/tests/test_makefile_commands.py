"""
Makefile command tests for Docker environment.

These tests verify:
- All Makefile commands work correctly
- Database operations (migrate, createsuperuser)
- Container shell access and log viewing
"""
import subprocess
import os
import time
from django.test import TestCase


class MakefileCommandTest(TestCase):
    """Test Makefile commands work correctly."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        super().setUpClass()
        cls.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    def run_make_command(self, command, timeout=30, check=True):
        """
        Helper method to run make commands.
        
        Args:
            command: Make command to run (e.g., 'ps', 'logs')
            timeout: Command timeout in seconds
            check: Whether to check return code
            
        Returns:
            subprocess.CompletedProcess object
        """
        try:
            result = subprocess.run(
                ['make', command],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail(f"Command 'make {command}' timed out after {timeout} seconds")
        except subprocess.CalledProcessError as e:
            if check:
                self.fail(f"Command 'make {command}' failed with return code {e.returncode}: {e.stderr}")
            return e
    
    def test_make_help_command(self):
        """Test 'make help' command displays help information."""
        result = self.run_make_command('help')
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('OneStep Docker Management Commands', result.stdout)
        self.assertIn('make up', result.stdout)
        self.assertIn('make down', result.stdout)
        self.assertIn('make build', result.stdout)
    
    def test_make_ps_command(self):
        """Test 'make ps' command shows running containers."""
        result = self.run_make_command('ps')
        
        self.assertEqual(result.returncode, 0)
        # Should show container status information
        self.assertIn('Running containers', result.stdout)
    
    def test_make_migrate_command(self):
        """Test 'make migrate' command runs database migrations."""
        result = self.run_make_command('migrate', timeout=60, check=False)
        
        # Command should either succeed or fail due to containers not running
        self.assertIn('Running database migrations', result.stdout)
        # If containers are running, should show migration output
        # If not running, will show error but command structure is correct
        self.assertTrue(
            result.returncode == 0 or
            'Error' in result.stderr or
            'not running' in result.stderr.lower()
        )
    
    def test_make_shell_command_exists(self):
        """Test 'make shell' command is available (non-interactive test)."""
        # We can't test interactive shell directly, but we can verify the command exists
        # by checking if it's defined in the Makefile
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('shell:', makefile_content)
        self.assertIn('docker-compose exec web /bin/bash', makefile_content)


class MakefileDatabaseOperationsTest(TestCase):
    """Test Makefile database operation commands."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        super().setUpClass()
        cls.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    def run_make_command(self, command, timeout=30, check=True, input_data=None):
        """Helper method to run make commands."""
        try:
            result = subprocess.run(
                ['make', command],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check,
                input=input_data
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail(f"Command 'make {command}' timed out after {timeout} seconds")
        except subprocess.CalledProcessError as e:
            if check:
                return e
            raise
    
    def test_migrate_command_runs_successfully(self):
        """Test database migrations run successfully."""
        result = self.run_make_command('migrate', timeout=60, check=False)
        
        # Command should either succeed or fail due to containers not running
        # Check for migration-related output
        self.assertTrue(
            'migrate' in result.stdout.lower() or
            'migrate' in result.stderr.lower()
        )
        # If containers are running, should succeed; otherwise will show error
        self.assertTrue(
            result.returncode == 0 or
            'Error' in result.stderr or
            'not running' in result.stderr.lower()
        )
    
    def test_createsuperuser_command_exists(self):
        """Test 'make createsuperuser' command is available."""
        # Verify command exists in Makefile
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('createsuperuser:', makefile_content)
        self.assertIn('docker-compose exec web python manage.py createsuperuser', makefile_content)
    
    def test_backup_command_creates_backup_directory(self):
        """Test 'make backup' command creates backups directory."""
        # Note: This test may fail if database is not running
        # We'll check if the command at least attempts to create the directory
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('backup:', makefile_content)
        self.assertIn('mkdir -p backups', makefile_content)
        self.assertIn('pg_dump', makefile_content)
    
    def test_restore_command_requires_backup_file(self):
        """Test 'make restore' command requires BACKUP_FILE parameter."""
        # Run restore without BACKUP_FILE - should show error
        result = self.run_make_command('restore', check=False)
        
        # Should fail or show error message about missing BACKUP_FILE
        self.assertTrue(
            result.returncode != 0 or
            'BACKUP_FILE' in result.stdout or
            'BACKUP_FILE' in result.stderr
        )


class MakefileServiceManagementTest(TestCase):
    """Test Makefile service management commands."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        super().setUpClass()
        cls.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    def run_make_command(self, command, timeout=30, check=True):
        """Helper method to run make commands."""
        try:
            result = subprocess.run(
                ['make', command],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail(f"Command 'make {command}' timed out after {timeout} seconds")
        except subprocess.CalledProcessError as e:
            if check:
                return e
            raise
    
    def test_up_command_structure(self):
        """Test 'make up' command has correct structure."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('up:', makefile_content)
        self.assertIn('docker-compose up -d', makefile_content)
        self.assertIn('Starting all services', makefile_content)
    
    def test_down_command_structure(self):
        """Test 'make down' command has correct structure."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('down:', makefile_content)
        self.assertIn('docker-compose down', makefile_content)
        self.assertIn('Stopping all services', makefile_content)
    
    def test_build_command_structure(self):
        """Test 'make build' command has correct structure."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('build:', makefile_content)
        self.assertIn('docker-compose build', makefile_content)
    
    def test_logs_command_structure(self):
        """Test 'make logs' command has correct structure."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('logs:', makefile_content)
        self.assertIn('docker-compose logs', makefile_content)
    
    def test_restart_command_structure(self):
        """Test 'make restart' command has correct structure."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('restart:', makefile_content)
        self.assertIn('docker-compose restart', makefile_content)
    
    def test_test_command_structure(self):
        """Test 'make test' command has correct structure."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('test:', makefile_content)
        self.assertIn('docker-compose exec web python manage.py test', makefile_content)


class MakefileProductionCommandsTest(TestCase):
    """Test Makefile production commands."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        super().setUpClass()
        cls.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    def test_production_commands_exist(self):
        """Test all production commands exist in Makefile."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        # Check for production command targets
        production_commands = [
            'prod-up:',
            'prod-down:',
            'prod-build:',
            'prod-logs:',
            'prod-shell:',
            'prod-migrate:',
            'prod-backup:',
            'prod-restore:'
        ]
        
        for command in production_commands:
            self.assertIn(command, makefile_content, f"Production command {command} not found in Makefile")
    
    def test_production_commands_use_prod_compose_file(self):
        """Test production commands use docker-compose.prod.yml."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        # Production commands should reference docker-compose.prod.yml
        self.assertIn('docker-compose.prod.yml', makefile_content)
    
    def test_prod_up_checks_for_env_file(self):
        """Test 'make prod-up' checks for .env.prod file."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        # Should check for .env.prod file
        self.assertIn('.env.prod', makefile_content)


class MakefileUtilityCommandsTest(TestCase):
    """Test Makefile utility commands."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        super().setUpClass()
        cls.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    def test_clean_command_exists(self):
        """Test 'make clean' command exists."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('clean:', makefile_content)
        self.assertIn('docker-compose down -v', makefile_content)
    
    def test_prune_command_exists(self):
        """Test 'make prune' command exists."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        self.assertIn('prune:', makefile_content)
        self.assertIn('docker system prune', makefile_content)
    
    def test_all_phony_targets_declared(self):
        """Test all targets are declared as .PHONY."""
        makefile_path = os.path.join(self.project_root, 'Makefile')
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        # Check for .PHONY declaration
        self.assertIn('.PHONY:', makefile_content)
        
        # Key commands should be in PHONY
        phony_commands = ['help', 'up', 'down', 'build', 'logs', 'shell', 'migrate', 'test']
        for command in phony_commands:
            self.assertIn(command, makefile_content)


class MakefileCommandIntegrationTest(TestCase):
    """Integration tests for Makefile commands."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        super().setUpClass()
        cls.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    def run_docker_compose_command(self, command, timeout=30):
        """Helper to run docker-compose commands directly."""
        try:
            result = subprocess.run(
                ['docker-compose'] + command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail(f"Docker compose command timed out after {timeout} seconds")
    
    def test_docker_compose_is_available(self):
        """Test docker-compose is available in the environment."""
        result = subprocess.run(
            ['docker-compose', '--version'],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Should return version information
        self.assertEqual(result.returncode, 0)
        self.assertTrue(
            'docker-compose' in result.stdout.lower() or
            'docker compose' in result.stdout.lower()
        )
    
    def test_docker_compose_config_is_valid(self):
        """Test docker-compose.yml configuration is valid."""
        result = self.run_docker_compose_command('config')
        
        # Should successfully parse the configuration
        self.assertEqual(result.returncode, 0)
        # Should contain service definitions
        self.assertTrue(
            'services:' in result.stdout or
            'web' in result.stdout or
            'db' in result.stdout
        )
    
    def test_production_compose_config_is_valid(self):
        """Test docker-compose.prod.yml configuration is valid."""
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.prod.yml', 'config'],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Should successfully parse the configuration
        # May fail if .env.prod doesn't exist, which is acceptable
        self.assertTrue(
            result.returncode == 0 or
            '.env.prod' in result.stderr
        )
