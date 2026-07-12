"""
Smart Skill Pool - Phase 2 Core Component

Auto-discovers, lazy-loads, and manages 107+ skills from skill-library.
Efficient memory management with cleanup after use.
"""

import sys
import logging
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from datetime import datetime
import inspect

logger = logging.getLogger(__name__)

SKILL_LIBRARY_PATH = Path("/home/vali/projects/skill-library")


@dataclass
class SkillMetadata:
    """Metadata about a skill."""
    name: str
    module_name: str
    class_name: str
    version: str = "1.0.0"
    description: str = ""
    category: str = ""
    loaded: bool = False
    instance: Optional[Any] = None
    last_used: Optional[str] = None

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name


@dataclass
class SkillPool:
    """Smart pool of available skills."""
    skills: Dict[str, SkillMetadata] = field(default_factory=dict)
    loaded_count: int = 0
    total_count: int = 0
    discovery_complete: bool = False

    def add_skill(self, metadata: SkillMetadata):
        """Add a skill to the pool."""
        self.skills[metadata.name] = metadata
        self.total_count = len(self.skills)

    def get_skill(self, name: str) -> Optional[SkillMetadata]:
        """Get skill by name."""
        return self.skills.get(name)

    def list_skills(self) -> List[SkillMetadata]:
        """List all skills in pool."""
        return list(self.skills.values())

    def list_loaded_skills(self) -> List[SkillMetadata]:
        """List currently loaded skills."""
        return [s for s in self.skills.values() if s.loaded]


class SkillLoader:
    """Loads and manages skills from skill-library."""

    def __init__(self, skill_library_path: str = str(SKILL_LIBRARY_PATH)):
        """Initialize skill loader.

        Args:
            skill_library_path: Path to skill-library directory
        """
        self.library_path = Path(skill_library_path)
        self.pool = SkillPool()
        self.cache = {}  # Cache loaded modules to avoid re-imports

        if not self.library_path.exists():
            raise ValueError(f"Skill library not found: {skill_library_path}")

        logger.info(f"Initialized SkillLoader for {skill_library_path}")

    def discover_all_skills(self) -> SkillPool:
        """Auto-discover all skills in library.

        Returns:
            SkillPool with all discovered skills
        """
        if self.pool.discovery_complete:
            logger.info(f"Using cached skill pool: {self.pool.total_count} skills")
            return self.pool

        logger.info("Discovering skills in library...")

        # Scan library directory
        for skill_dir in sorted(self.library_path.iterdir()):
            if not skill_dir.is_dir():
                continue

            # Skip special directories
            if skill_dir.name.startswith('.') or skill_dir.name in {'scripts', 'commands'}:
                continue

            # Check if it's a valid skill (has __init__.py and core.py)
            init_file = skill_dir / "__init__.py"
            core_file = skill_dir / "core.py"

            if init_file.exists() and core_file.exists():
                try:
                    metadata = self._extract_skill_metadata(skill_dir)
                    self.pool.add_skill(metadata)
                    logger.debug(f"Discovered skill: {metadata.name}")
                except Exception as e:
                    logger.warning(f"Could not load skill metadata from {skill_dir.name}: {e}")

        self.pool.discovery_complete = True
        logger.info(f"Discovery complete: {self.pool.total_count} skills found")

        return self.pool

    def _extract_skill_metadata(self, skill_dir: Path) -> SkillMetadata:
        """Extract metadata from a skill directory.

        Args:
            skill_dir: Path to skill directory

        Returns:
            SkillMetadata object
        """
        skill_name = skill_dir.name
        module_name = skill_name.replace('-', '_')

        # Try to read version from __init__.py
        init_file = skill_dir / "__init__.py"
        version = "1.0.0"

        if init_file.exists():
            try:
                content = init_file.read_text()
                # Look for __version__
                for line in content.split('\n'):
                    if '__version__' in line and '=' in line:
                        version = line.split('=')[1].strip().strip('"').strip("'")
                        break
            except Exception:
                pass

        # Determine class name (CamelCase from module name)
        class_name = self._to_class_name(module_name)

        # Read description from README
        description = ""
        readme_file = skill_dir / "README.md"
        if readme_file.exists():
            try:
                content = readme_file.read_text()
                # Get first line
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                if lines:
                    description = lines[0][:200]  # First 200 chars
            except Exception:
                pass

        # Determine category from skill name
        category = self._extract_category(skill_name)

        return SkillMetadata(
            name=skill_name,
            module_name=module_name,
            class_name=class_name,
            version=version,
            description=description,
            category=category
        )

    @staticmethod
    def _to_class_name(snake_case: str) -> str:
        """Convert snake_case to CamelCase.

        Args:
            snake_case: String in snake_case

        Returns:
            CamelCase string
        """
        return ''.join(word.capitalize() for word in snake_case.split('_'))

    @staticmethod
    def _extract_category(skill_name: str) -> str:
        """Extract category from skill name.

        Args:
            skill_name: Skill directory name

        Returns:
            Category string
        """
        # Remove version suffix (v2, v3, etc.)
        base_name = skill_name.split('-v')[0]
        return base_name

    def load_skill(self, skill_name: str) -> Optional[Any]:
        """Lazy-load a single skill.

        Args:
            skill_name: Name of skill to load

        Returns:
            Skill instance or None if load fails
        """
        metadata = self.pool.get_skill(skill_name)

        if not metadata:
            logger.error(f"Skill not found: {skill_name}")
            return None

        if metadata.loaded and metadata.instance:
            logger.debug(f"Skill already loaded: {skill_name}")
            return metadata.instance

        try:
            logger.info(f"Loading skill: {skill_name}...")

            # Add library to path
            if str(self.library_path) not in sys.path:
                sys.path.insert(0, str(self.library_path))

            # Check cache first
            cache_key = f"{skill_name}.{metadata.class_name}"
            if cache_key in self.cache:
                logger.debug(f"Skill loaded from cache: {skill_name}")
                instance = self.cache[cache_key]
            else:
                # Import using spec (more reliable)
                skill_path = self.library_path / skill_name
                spec = importlib.util.spec_from_file_location(
                    metadata.module_name,
                    skill_path / "__init__.py"
                )

                if not spec or not spec.loader:
                    logger.error(f"Could not create spec for {skill_name}")
                    return None

                module = importlib.util.module_from_spec(spec)
                sys.modules[metadata.module_name] = module
                spec.loader.exec_module(module)

                # Get the class
                if not hasattr(module, metadata.class_name):
                    logger.error(f"Class {metadata.class_name} not found in {skill_name}")
                    return None

                skill_class = getattr(module, metadata.class_name)

                # Instantiate
                instance = skill_class()
                self.cache[cache_key] = instance

            # Update metadata
            metadata.instance = instance
            metadata.loaded = True
            metadata.last_used = datetime.now().isoformat()
            self.pool.loaded_count += 1

            logger.info(f"Skill loaded successfully: {skill_name}")
            return instance

        except Exception as e:
            logger.error(f"Error loading skill {skill_name}: {e}", exc_info=True)
            return None

    def unload_skill(self, skill_name: str) -> bool:
        """Unload a skill (cleanup).

        Args:
            skill_name: Name of skill to unload

        Returns:
            True if successful
        """
        metadata = self.pool.get_skill(skill_name)

        if not metadata or not metadata.loaded:
            logger.debug(f"Skill not loaded or not found: {skill_name}")
            return False

        try:
            logger.info(f"Unloading skill: {skill_name}...")

            metadata.instance = None
            metadata.loaded = False
            self.pool.loaded_count = max(0, self.pool.loaded_count - 1)

            logger.info(f"Skill unloaded: {skill_name}")
            return True

        except Exception as e:
            logger.error(f"Error unloading skill {skill_name}: {e}")
            return False

    def execute_skill(self, skill_name: str, method_name: str = "analyze", **kwargs) -> Optional[Dict[str, Any]]:
        """Load, execute, and unload a skill (safe lifecycle).

        Args:
            skill_name: Name of skill to execute
            method_name: Method to call on skill (default: analyze)
            **kwargs: Arguments to pass to method

        Returns:
            Method result or None if failed
        """
        try:
            # Load skill
            instance = self.load_skill(skill_name)
            if not instance:
                return None

            # Check if method exists
            if not hasattr(instance, method_name):
                logger.error(f"Method {method_name} not found in skill {skill_name}")
                self.unload_skill(skill_name)
                return None

            # Execute method
            method = getattr(instance, method_name)
            result = method(**kwargs)

            # Unload skill (cleanup)
            self.unload_skill(skill_name)

            return result

        except Exception as e:
            logger.error(f"Error executing skill {skill_name}: {e}", exc_info=True)
            self.unload_skill(skill_name)
            return None

    def filter_skills_by_category(self, category: str) -> List[SkillMetadata]:
        """Filter skills by category.

        Args:
            category: Category name (e.g., 'best-practices-applier')

        Returns:
            List of matching skills
        """
        return [s for s in self.pool.list_skills() if s.category == category]

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a skill.

        Args:
            skill_name: Name of skill

        Returns:
            Dictionary with skill info
        """
        metadata = self.pool.get_skill(skill_name)

        if not metadata:
            return None

        return {
            'name': metadata.name,
            'version': metadata.version,
            'category': metadata.category,
            'description': metadata.description,
            'loaded': metadata.loaded,
            'last_used': metadata.last_used,
            'module': metadata.module_name,
            'class': metadata.class_name,
        }


# Test usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    try:
        # Initialize loader
        loader = SkillLoader()

        # Discover all skills
        print("\n1️⃣ Discovering skills...")
        pool = loader.discover_all_skills()
        print(f"✓ Total skills: {pool.total_count}")
        print(f"✓ Loaded: {pool.loaded_count}")
        print(f"✓ Available: {pool.total_count - pool.loaded_count}")

        # List first 10 skills
        print("\n2️⃣ First 10 skills:")
        for skill in pool.list_skills()[:10]:
            print(f"  - {skill.name} (v{skill.version}): {skill.description[:60]}")

        # Filter by category
        print("\n3️⃣ Skills by category:")
        categories = {}
        for skill in pool.list_skills():
            if skill.category not in categories:
                categories[skill.category] = 0
            categories[skill.category] += 1

        for cat in sorted(categories.keys())[:10]:
            print(f"  - {cat}: {categories[cat]} skills")

        # Try to load a skill
        print("\n4️⃣ Testing skill load/unload...")
        test_skill = pool.list_skills()[0].name
        print(f"  Loading: {test_skill}")
        instance = loader.load_skill(test_skill)
        if instance:
            print(f"  ✓ Loaded successfully")
            print(f"  ✓ Instance type: {type(instance).__name__}")

            # Unload
            loader.unload_skill(test_skill)
            print(f"  ✓ Unloaded successfully")

        print("\n✓ Skill pool test PASSED\n")

    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
