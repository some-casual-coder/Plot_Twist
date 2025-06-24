from .user_models import User, UserProvider
from .style_models import ImageStyle
from .badge_models import Badge  # Badge is referenced by UserBadge

# Then models that reference the ones above
from .badge_models import UserBadge  # UserBadge references User and Badge
# If UserBadge was in a separate file, ensure User and Badge are "known"

from .mystery_models import DailyMystery
from .mystery_models import UserMysterySession
