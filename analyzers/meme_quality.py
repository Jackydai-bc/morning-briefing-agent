"""
Meme币质检分析器 - Meme Quality Analyzer
对meme币进行质量检查和风险评估
"""

from typing import Dict, List, Optional


class MemeQualityAnalyzer:
    """Meme币质检分析器"""

    def __init__(self, config: Dict):
        self.config = config
        self.quality_check = config.get("MEME_QUALITY_CHECK", {})
        self.new_token_filters = config.get("NEW_TOKEN_FILTERS", {})

    def analyze_token(self, token: Dict) -> Dict:
        """
        分析单个代币的质量

        Args:
            token: 代币数据

        Returns:
            {
                "grade": "S/A/B/C/D",
                "score": 85,
                "checks": {
                    "交易量": {"pass": True, "value": 100000},
                    "流动性": {"pass": True, "value": 50000},
                    ...
                },
                "warnings": ["警告1", "警告2"],
                "recommendation": "建议",
            }
        """
        checks = {}
        warnings = []
        score = 0
        total_checks = 0

        # 1. 交易量检查
        volume = token.get("volume_24h", 0)
        min_volume = self.quality_check.get("最小交易量", 50000)
        volume_pass = volume >= min_volume
        checks["交易量"] = {"pass": volume_pass, "value": volume}
        total_checks += 1
        if volume_pass:
            score += 20
        else:
            warnings.append(f"交易量过低: ${volume:,.0f}")

        # 2. 持有者数量
        holders = token.get("holders", 0)
        min_holders = self.quality_check.get("最小持有者", 100)
        holders_pass = holders >= min_holders
        checks["持有者"] = {"pass": holders_pass, "value": holders}
        total_checks += 1
        if holders_pass:
            score += 20
        else:
            warnings.append(f"持有者过少: {holders}")

        # 3. 流动性
        liquidity = token.get("liquidity", 0)
        min_liquidity = self.quality_check.get("最小流动性", 10000)
        liquidity_pass = liquidity >= min_liquidity
        checks["流动性"] = {"pass": liquidity_pass, "value": liquidity}
        total_checks += 1
        if liquidity_pass:
            score += 20
        else:
            warnings.append(f"流动性不足: ${liquidity:,.0f}")

        # 4. LP锁定
        lp_locked = token.get("lp_locked", False)
        lp_lock_pct = token.get("lp_lock_pct", 0)
        min_lp_lock = self.quality_check.get("最小LP锁定", 80)
        lp_pass = lp_lock_pct >= min_lp_lock
        checks["LP锁定"] = {"pass": lp_pass, "value": f"{lp_lock_pct}%"}
        total_checks += 1
        if lp_pass:
            score += 20
        else:
            warnings.append(f"LP未完全锁定: {lp_lock_pct}%")

        # 5. Top10持仓
        # 这个数据需要链上查询，暂时跳过
        score += 20  # 默认给分
        total_checks += 1

        # 计算评级
        grade = self._calculate_grade(score)

        # 生成建议
        recommendation = self._generate_recommendation(grade, warnings)

        return {
            "symbol": token.get("symbol"),
            "grade": grade,
            "score": int(score),
            "checks": checks,
            "warnings": warnings,
            "recommendation": recommendation,
        }

    def _calculate_grade(self, score: int) -> str:
        """根据分数计算评级"""
        if score >= 90:
            return "S"
        elif score >= 75:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 40:
            return "C"
        else:
            return "D"

    def _generate_recommendation(self, grade: str, warnings: List[str]) -> str:
        """生成投资建议"""
        if grade == "S":
            return "优质，可以考虑小仓位参与"
        elif grade == "A":
            return "良好，可以关注"
        elif grade == "B":
            return "一般，谨慎参与"
        elif grade == "C":
            return "风险较高，建议观望"
        else:
            return "高风险，不建议参与"

    def batch_analyze(self, tokens: List[Dict]) -> List[Dict]:
        """
        批量分析代币

        Args:
            tokens: 代币列表

        Returns:
            分析结果列表
        """
        results = []

        for token in tokens:
            try:
                analysis = self.analyze_token(token)
                results.append(analysis)
            except Exception as e:
                continue

        return results

    def filter_by_grade(self, analyses: List[Dict], min_grade: str = "B") -> List[Dict]:
        """
        按评级过滤

        Args:
            analyses: 分析结果列表
            min_grade: 最低评级

        Returns:
            过滤后的列表
        """
        grade_order = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1}
        min_score = grade_order.get(min_grade, 3)

        return [a for a in analyses if grade_order.get(a.get("grade", "D"), 1) >= min_score]

    def get_summary(self, analyses: List[Dict]) -> Dict:
        """
        获取质检摘要

        Args:
            analyses: 分析结果列表

        Returns:
            摘要统计
        """
        grade_counts = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0}

        for analysis in analyses:
            grade = analysis.get("grade", "D")
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        return {
            "total": len(analyses),
            "grade_distribution": grade_counts,
            "pass_rate": (grade_counts["S"] + grade_counts["A"] + grade_counts["B"]) / len(analyses) * 100 if analyses else 0,
        }
