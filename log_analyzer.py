import numpy as np
from datetime import datetime, timedelta
import re
from collections import Counter, defaultdict
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import pandas as pd
from typing import List, Dict, Tuple


class LogAnalyzer:
    def __init__(self):
        self.error_patterns = defaultdict(int)
        self.transaction_times = []
        self.transaction_volumes = defaultdict(int)
        self.common_error_sequences = defaultdict(list)

    def extract_timestamp(self, log_line: str) -> datetime:
        """Extract timestamp from log line."""
        timestamp_match = re.search(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}", log_line)
        if timestamp_match:
            return datetime.strptime(timestamp_match.group(), "%Y-%m-%d %H:%M:%S")
        return None

    def analyze_error_patterns(self, errors: List[str]) -> Dict:
        """Analyze error patterns and identify common causes."""
        error_analysis = {
            "common_patterns": [],
            "time_based_patterns": [],
            "recommendations": [],
        }

        # Analyze error frequencies
        error_types = Counter([self._categorize_error(error) for error in errors])
        error_analysis["common_patterns"] = error_types.most_common()

        # Identify time-based patterns
        if len(self.transaction_times) > 0:
            peak_times = self._analyze_peak_times()
            error_analysis["time_based_patterns"] = peak_times

        # Generate recommendations
        error_analysis["recommendations"] = self._generate_recommendations(error_types)

        return error_analysis

    def analyze_transaction_patterns(
        self, successful_txns: List[str], failed_txns: List[str]
    ) -> Dict:
        """Analyze transaction patterns to identify anomalies and trends."""
        analysis = {
            "success_rate": 0.0,
            "peak_hours": [],
            "anomalies": [],
            "recommendations": [],
        }

        total_txns = len(successful_txns) + len(failed_txns)
        if total_txns > 0:
            analysis["success_rate"] = (len(successful_txns) / total_txns) * 100

        # Process timestamps from transactions
        timestamps = []
        for txn in successful_txns + failed_txns:
            ts = self.extract_timestamp(txn)
            if ts:
                timestamps.append(ts)
                self.transaction_times.append(ts)  # Store for overall analysis

        # Analyze hourly volumes
        hourly_volumes = self._analyze_hourly_volumes(timestamps)
        analysis["peak_hours"] = self._identify_peak_hours(hourly_volumes)

        # Detect anomalies using DBSCAN
        if hourly_volumes:
            anomalies = self._detect_anomalies(list(hourly_volumes.values()))
            analysis["anomalies"] = anomalies

        # Generate transaction-specific recommendations
        analysis["recommendations"] = self._generate_transaction_recommendations(
            analysis["success_rate"], analysis["peak_hours"], analysis["anomalies"]
        )

        return analysis

    def _analyze_hourly_volumes(self, timestamps: List[datetime]) -> Dict[int, int]:
        """Analyze transaction volumes by hour."""
        hourly_volumes = defaultdict(int)
        for ts in timestamps:
            if ts:  # Make sure timestamp is not None
                hourly_volumes[ts.hour] += 1
        return dict(sorted(hourly_volumes.items()))

    def _identify_peak_hours(self, hourly_volumes: Dict[int, int]) -> List[Dict]:
        """Identify peak transaction hours."""
        if not hourly_volumes:
            return []

        sorted_hours = sorted(hourly_volumes.items(), key=lambda x: x[1], reverse=True)
        peak_hours = []

        for hour, volume in sorted_hours[:3]:  # Get top 3 peak hours
            peak_hours.append({"hour": hour, "volume": volume})

        return peak_hours

    def analyze_sms_delivery(self, sms_logs: List[str]) -> Dict:
        """Analyze SMS delivery patterns and performance."""
        analysis = {
            "delivery_rate": 0.0,
            "latency_patterns": [],
            "carrier_performance": {},
            "recommendations": [],
        }

        # Calculate delivery success rate
        successful_delivery = sum(1 for log in sms_logs if "200 OK" in log)
        total_attempts = len(sms_logs)
        if total_attempts > 0:
            analysis["delivery_rate"] = (successful_delivery / total_attempts) * 100

        # Analyze delivery latency
        latencies = self._calculate_sms_latencies(sms_logs)
        analysis["latency_patterns"] = self._analyze_latency_patterns(latencies)

        # Analyze carrier performance
        analysis["carrier_performance"] = self._analyze_carrier_performance(sms_logs)

        # Generate recommendations
        analysis["recommendations"] = self._generate_sms_recommendations(analysis)

        return analysis

    def _analyze_latency_patterns(self, latencies: List[float]) -> Dict:
        """Analyze patterns in SMS delivery latencies."""
        if not latencies:
            return {"average": 0, "median": 0, "p95": 0}

        return {
            "average": np.mean(latencies),
            "median": np.median(latencies),
            "p95": np.percentile(latencies, 95),
        }

    def _analyze_carrier_performance(self, sms_logs: List[str]) -> Dict:
        """Analyze performance by carrier."""
        carrier_stats = defaultdict(lambda: {"total": 0, "successful": 0})

        for log in sms_logs:
            # Extract carrier info (modify regex pattern based on your log format)
            carrier_match = re.search(r"carrier[:\s]+(\w+)", log, re.IGNORECASE)
            if carrier_match:
                carrier = carrier_match.group(1)
                carrier_stats[carrier]["total"] += 1
                if "200 OK" in log:
                    carrier_stats[carrier]["successful"] += 1

        # Calculate success rates
        performance = {}
        for carrier, stats in carrier_stats.items():
            if stats["total"] > 0:
                performance[carrier] = {
                    "success_rate": (stats["successful"] / stats["total"]) * 100,
                    "total_messages": stats["total"],
                }

        return performance

    def _generate_sms_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations for SMS delivery improvement."""
        recommendations = []

        if analysis["delivery_rate"] < 98:
            recommendations.append(
                "SMS delivery rate is below optimal levels. Consider implementing "
                "retry mechanisms and monitoring carrier performance."
            )

        if analysis.get("latency_patterns", {}).get("p95", 0) > 10:
            recommendations.append(
                "High SMS delivery latency detected. Review carrier connections "
                "and consider using multiple providers for redundancy."
            )

        for carrier, stats in analysis.get("carrier_performance", {}).items():
            if stats.get("success_rate", 0) < 95:
                recommendations.append(
                    f"Low success rate ({stats['success_rate']:.1f}%) detected for "
                    f"carrier {carrier}. Consider reviewing carrier configuration."
                )

        return recommendations

    def _categorize_error(self, error: str) -> str:
        """Categorize error messages into common patterns."""
        if "NO RECORD ON FILE" in error.upper():
            return "INVALID_ACCOUNT"
        elif "EXCEEDS ACCOUNT AMOUNT LIMIT" in error.upper():
            return "LIMIT_EXCEEDED"
        elif "SYSTEM FAILURE" in error.upper():
            return "SYSTEM_ERROR"
        elif "HTTP Status Code: " in error:
            return f"HTTP_ERROR_{error.split('HTTP Status Code: ')[1].split()[0]}"
        return "OTHER"

    def _analyze_peak_times(self) -> List[Dict]:
        """Analyze peak transaction times."""
        hour_counts = Counter([dt.hour for dt in self.transaction_times])
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [{"hour": hour, "count": count} for hour, count in peak_hours]

    def _detect_anomalies(self, volumes: List[int]) -> List[Dict]:
        """Detect anomalous transaction patterns using DBSCAN."""
        if len(volumes) < 2:
            return []

        X = np.array(volumes).reshape(-1, 1)
        X_scaled = StandardScaler().fit_transform(X)

        clustering = DBSCAN(eps=0.5, min_samples=2).fit(X_scaled)
        anomalies = []

        for i, label in enumerate(clustering.labels_):
            if label == -1:  # Anomaly detected
                anomalies.append(
                    {"hour": i, "volume": volumes[i], "deviation": abs(X_scaled[i][0])}
                )

        return sorted(anomalies, key=lambda x: x["deviation"], reverse=True)

    def _calculate_sms_latencies(self, sms_logs: List[str]) -> List[float]:
        """Calculate SMS delivery latencies."""
        latencies = []
        for log in sms_logs:
            send_time = self.extract_timestamp(log)
            if "200 OK" in log:
                delivery_time = self.extract_timestamp(log.split("200 OK")[1])
                if send_time and delivery_time:
                    latency = (delivery_time - send_time).total_seconds()
                    latencies.append(latency)
        return latencies

    def get_ai_insights(
        self, springboot_logs: List[str], database_logs: List[str], sms_logs: List[str]
    ) -> Dict:
        """Generate comprehensive AI insights from all log sources."""
        insights = {
            "error_analysis": self.analyze_error_patterns(
                [log for log in springboot_logs + database_logs if self._is_error(log)]
            ),
            "transaction_analysis": self.analyze_transaction_patterns(
                [log for log in database_logs if "TS" in log],
                [log for log in database_logs if "TF" in log],
            ),
            "sms_analysis": self.analyze_sms_delivery(sms_logs),
            "overall_recommendations": [],
        }

        # Generate overall recommendations
        insights["overall_recommendations"] = self._generate_overall_recommendations(
            insights
        )

        return insights

    def _is_error(self, log: str) -> bool:
        """Check if a log line represents an error."""
        error_indicators = [
            "ERROR",
            "FAILED",
            "EXCEPTION",
            "HTTP Status Code: [45]",
            "NO RECORD ON FILE",
            "SYSTEM FAILURE",
        ]
        return any(indicator in log.upper() for indicator in error_indicators)

    def _generate_recommendations(self, error_types: Counter) -> List[str]:
        """Generate recommendations based on error patterns."""
        recommendations = []

        if error_types["INVALID_ACCOUNT"] > 0:
            recommendations.append(
                "High number of invalid account errors detected. Consider implementing "
                "pre-validation checks and account verification before processing."
            )

        if error_types["LIMIT_EXCEEDED"] > 0:
            recommendations.append(
                "Multiple limit exceeded errors observed. Consider adding real-time "
                "balance checks and implementing soft warnings when approaching limits."
            )

        if error_types["SYSTEM_ERROR"] > 0:
            recommendations.append(
                "System errors detected. Review system capacity and consider scaling "
                "resources during peak hours."
            )

        return recommendations

    def _generate_overall_recommendations(self, insights: Dict) -> List[str]:
        """Generate overall system recommendations based on all insights."""
        recommendations = []

        # Analyze error patterns
        if insights["error_analysis"]["common_patterns"]:
            top_error = insights["error_analysis"]["common_patterns"][0]
            recommendations.append(
                f"Primary error pattern identified: {top_error[0]}. "
                "Consider implementing targeted error handling and prevention."
            )

        # Analyze transaction success rate
        txn_analysis = insights["transaction_analysis"]
        if txn_analysis["success_rate"] < 95:
            recommendations.append(
                "Transaction success rate needs improvement. "
                "Consider implementing additional validation and error handling."
            )

        # Analyze SMS delivery performance
        sms_analysis = insights["sms_analysis"]
        if sms_analysis["delivery_rate"] < 98:
            recommendations.append(
                "SMS delivery rate is below optimal levels. "
                "Review SMS gateway configuration and implement retry mechanisms."
            )

        return recommendations

    def _generate_transaction_recommendations(
        self, success_rate: float, peak_hours: List[Dict], anomalies: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on transaction patterns."""
        recommendations = []

        # Success rate recommendations
        if success_rate < 95:
            recommendations.append(
                "Transaction success rate is below 95%. Consider reviewing transaction "
                "handling logic and implementing additional error handling."
            )

        # Peak hours recommendations
        if peak_hours:
            peak_hour = peak_hours[0]["hour"]
            recommendations.append(
                f"Peak transaction volume observed at hour {peak_hour}. Consider "
                "allocating additional resources during this time."
            )

        # Anomaly recommendations
        for anomaly in anomalies:
            if anomaly["deviation"] > 2:  # Significant deviation
                recommendations.append(
                    f"Unusual transaction volume detected at hour {anomaly['hour']}. "
                    f"Volume: {anomaly['volume']}. Consider investigating potential causes."
                )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "Transaction patterns appear normal. Continue monitoring for any changes."
            )

        return recommendations
