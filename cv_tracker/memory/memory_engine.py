import logging
from config.settings import VEHICLE_THRESHOLD, CONGESTION_DURATION, COOLDOWN_DURATION, ZONE_CAPACITY

logger = logging.getLogger("MemoryEngine")


class MemoryEngine:
    """
    Engine that maintains temporal memory of vehicle counts inside the zone.
    Tracks state, detects congestion events, manages cooldowns, and records analytics.
    """

    def __init__(self):
        # Configuration constants loaded from settings
        self.threshold = VEHICLE_THRESHOLD
        self.required_duration = CONGESTION_DURATION
        self.cooldown_duration = COOLDOWN_DURATION
        self.zone_capacity = ZONE_CAPACITY

        # Temporal state variables
        self.congestion_start_time = None
        self.is_congested = False
        
        # Cooldown state variables
        self.last_event_time = -999.0      # Timestamp when last event was logged
        self.cooldown_end_time = -999.0    # Time when cooldown expires
        
        # Analytics state
        self.peak_vehicles = 0
        self.total_congested_frames_time = 0.0
        self.prev_elapsed_time = 0.0

    def update(self, vehicle_count: int, elapsed_seconds: float) -> dict:
        """
        Updates the memory engine state with the current vehicle count and elapsed time.

        :param vehicle_count: Number of vehicles currently inside the zone
        :param elapsed_seconds: Current time in the video (seconds since start)
        :return: A dictionary containing the updated state:
                 {
                     "vehicle_count": int,
                     "density_percentage": float,
                     "congestion_status": str,  # "CLEAR", "PENDING", "ACTIVE"
                     "timer_duration": float,
                     "cooldown_active": bool,
                     "cooldown_remaining": float,
                     "trigger_event": bool,
                     "analytics": {
                         "peak_vehicles": int,
                         "density_percentage": float
                     }
                 }
        """
        trigger_event = False
        status = "CLEAR"
        timer_duration = 0.0
        cooldown_remaining = max(0.0, self.cooldown_end_time - elapsed_seconds)
        cooldown_active = cooldown_remaining > 0.0

        # Update analytics: peak vehicles seen in the zone
        if vehicle_count > self.peak_vehicles:
            self.peak_vehicles = vehicle_count

        # Keep track of cumulative congestion time
        time_delta = elapsed_seconds - self.prev_elapsed_time
        if self.is_congested and time_delta > 0:
            self.total_congested_frames_time += time_delta
        self.prev_elapsed_time = elapsed_seconds

        # Core logic: check vehicle count against threshold
        if vehicle_count >= self.threshold:
            # If timer has not started, start it
            if self.congestion_start_time is None:
                self.congestion_start_time = elapsed_seconds
            
            timer_duration = elapsed_seconds - self.congestion_start_time
            
            # Determine status
            if self.is_congested:
                status = "ACTIVE"
            else:
                status = "PENDING"
                # Check if duration threshold is met
                if timer_duration >= self.required_duration:
                    # Check if cooldown has expired
                    if not cooldown_active:
                        trigger_event = True
                        self.is_congested = True
                        self.last_event_time = elapsed_seconds
                        status = "ACTIVE"
                        logger.info(
                            "Congestion threshold met for %.1f seconds. Event Triggered!",
                            timer_duration
                        )
                    else:
                        # In cooldown: status remains pending, wait until cooldown ends or count drops
                        logger.debug("Congestion threshold met but cooldown is active.")
        else:
            # Vehicle count dropped below threshold: reset timer
            self.congestion_start_time = None
            timer_duration = 0.0
            
            # If we were previously congested, clean state and initiate cooldown
            if self.is_congested:
                self.is_congested = False
                self.cooldown_end_time = elapsed_seconds + self.cooldown_duration
                cooldown_remaining = self.cooldown_duration
                cooldown_active = True
                logger.info("Congestion cleared. Cooldown initiated for %.1f seconds.", self.cooldown_duration)
            
            status = "CLEAR"

        # Calculate density percentage relative to configured zone capacity
        density = min(100.0, (vehicle_count / self.zone_capacity) * 100.0)

        return {
            "vehicle_count": vehicle_count,
            "density_percentage": density,
            "congestion_status": status,
            "timer_duration": timer_duration,
            "cooldown_active": cooldown_active,
            "cooldown_remaining": cooldown_remaining,
            "trigger_event": trigger_event,
            "analytics": {
                "peak_vehicles": self.peak_vehicles,
                "total_congested_time": self.total_congested_frames_time
            }
        }
