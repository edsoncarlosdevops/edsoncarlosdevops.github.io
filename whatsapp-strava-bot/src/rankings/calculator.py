from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict
import pytz


class RankingCalculator:
    """Calculate rankings for athletes based on their activities"""

    def __init__(self, timezone: str = 'America/Sao_Paulo'):
        self.timezone = pytz.timezone(timezone)

    def get_week_range(self, date: datetime = None) -> tuple:
        """Get start and end of the week (Monday to Sunday)"""
        if date is None:
            date = datetime.now(self.timezone)

        # Get Monday of the week
        start = date - timedelta(days=date.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

        # Get Sunday of the week
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)

        return start, end

    def get_month_range(self, date: datetime = None) -> tuple:
        """Get start and end of the month"""
        if date is None:
            date = datetime.now(self.timezone)

        # First day of the month
        start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Last day of the month
        if date.month == 12:
            end = date.replace(month=12, day=31, hour=23, minute=59, second=59)
        else:
            next_month = date.replace(month=date.month + 1, day=1)
            end = next_month - timedelta(seconds=1)

        return start, end

    def calculate_ranking(self, activities: List) -> List[Dict]:
        """
        Calculate ranking based on total distance

        Args:
            activities: List of Activity objects from database

        Returns:
            List of dicts with ranking information
        """
        athlete_stats = defaultdict(lambda: {
            'total_distance': 0.0,
            'total_runs': 0,
            'total_time': 0,
            'name': ''
        })

        for activity in activities:
            athlete_id = activity.athlete_strava_id
            athlete_stats[athlete_id]['name'] = activity.athlete_name
            athlete_stats[athlete_id]['total_distance'] += activity.distance
            athlete_stats[athlete_id]['total_runs'] += 1
            athlete_stats[athlete_id]['total_time'] += activity.moving_time or 0

        # Convert to list and sort by distance
        ranking = []
        for athlete_id, stats in athlete_stats.items():
            avg_pace = 0
            if stats['total_distance'] > 0 and stats['total_time'] > 0:
                # Calculate average pace in min/km
                avg_pace = (stats['total_time'] / 60) / stats['total_distance']

            ranking.append({
                'athlete_id': athlete_id,
                'name': stats['name'],
                'total_distance': round(stats['total_distance'], 2),
                'total_runs': stats['total_runs'],
                'total_time': stats['total_time'],
                'avg_pace': round(avg_pace, 2)
            })

        # Sort by total distance (descending)
        ranking.sort(key=lambda x: x['total_distance'], reverse=True)

        # Add position
        for idx, athlete in enumerate(ranking, 1):
            athlete['position'] = idx

        return ranking

    def format_time(self, seconds: int) -> str:
        """Format seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def format_ranking_message(self, ranking: List[Dict], period: str = "semanal") -> str:
        """
        Format ranking as a WhatsApp message

        Args:
            ranking: List of ranking data
            period: "semanal" or "mensal"

        Returns:
            Formatted message string
        """
        if not ranking:
            return f"📊 *Ranking {period.capitalize()}*\n\nNenhuma corrida registrada neste período."

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        message = f"📊 *Ranking {period.capitalize()} - Corridas*\n\n"

        for athlete in ranking:
            pos = athlete['position']
            medal = medals.get(pos, f"{pos}º")
            name = athlete['name']
            distance = athlete['total_distance']
            runs = athlete['total_runs']
            total_time = self.format_time(athlete['total_time'])
            avg_pace = athlete['avg_pace']

            message += f"{medal} *{name}*\n"
            message += f"   📏 {distance:.2f} km em {runs} corrida(s)\n"
            message += f"   ⏱️ Tempo total: {total_time}\n"
            message += f"   🏃 Pace médio: {avg_pace:.2f} min/km\n\n"

        return message

    def get_activity_notification(self, athlete_name: str, distance: float,
                                  moving_time: int, activity_name: str = None) -> str:
        """
        Format a notification message for a new activity

        Args:
            athlete_name: Name of the athlete
            distance: Distance in km
            moving_time: Moving time in seconds
            activity_name: Name of the activity

        Returns:
            Formatted notification message
        """
        time_str = self.format_time(moving_time)
        pace = (moving_time / 60) / distance if distance > 0 else 0

        message = f"🏃‍♂️ *Nova Corrida Registrada!*\n\n"
        message += f"👤 *{athlete_name}*\n"

        if activity_name:
            message += f"📝 {activity_name}\n"

        message += f"📏 Distância: *{distance:.2f} km*\n"
        message += f"⏱️ Tempo: {time_str}\n"
        message += f"🏃 Pace: {pace:.2f} min/km\n\n"
        message += "Parabéns! 👏🎉"

        return message
