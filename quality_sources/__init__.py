"""Quality source registry and manager."""
import logging

from quality_sources.base import QualitySource
from quality_sources.sample import SampleQualitySource
from shared import Car, QualityRating

__all__ = ["QualitySourceManager"]

logger = logging.getLogger(__name__)


class QualitySourceManager:
    """Orchestrates multiple quality data sources, merges ratings."""

    def __init__(self) -> None:
        """Initialize with registered sources."""
        self.sources: dict[str, QualitySource] = {}
        self._register_default_sources()

    def _register_default_sources(self) -> None:
        """Register built-in sources."""
        self.register(SampleQualitySource())
        # TODO: Register real sources as they're implemented
        # self.register(ADACSource())
        # self.register(TUVSource())
        # self.register(RepairNetworkSource())
        # self.register(BuyerReviewsSource())

    def register(self, source: QualitySource) -> None:
        """Register a new quality source.

        Args:
            source: Implementation of QualitySource protocol.
        """
        self.sources[source.source_name] = source
        logger.info(f"Registered quality source: {source.source_name}")

    def get_quality(self, car: Car, sources: list[str] | None = None) -> QualityRating | None:
        """Get merged quality rating from one or more sources.

        Args:
            car: Car to rate.
            sources: List of source names (None = all available). Uses first match.

        Returns:
            QualityRating merged from sources, or None if no source has data.
        """
        if sources is None:
            sources = list(self.sources.keys())

        for source_name in sources:
            if source_name not in self.sources:
                logger.warning(f"Quality source not found: {source_name}")
                continue

            source = self.sources[source_name]
            if not source.is_available():
                logger.warning(f"Quality source unavailable: {source_name}")
                continue

            try:
                quality = source.get_quality(car)
                if quality:
                    logger.debug(f"Got quality rating for {car.brand} {car.model} from {source_name}")
                    return quality
            except Exception as e:
                logger.error(f"Error getting quality from {source_name}: {e}")

        logger.debug(f"No quality data found for {car.brand} {car.model}")
        return None

    def get_source_metadata(self) -> dict[str, str]:
        """Return list of available quality sources."""
        return {name: source.source_name for name, source in self.sources.items()}
