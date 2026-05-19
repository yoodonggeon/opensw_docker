# backend/lotto/models.py
from django.db import models
from django.contrib.auth.models import User

class LottoRound(models.Model):
    """로또 추첨 회차 정보"""
    round_number = models.PositiveIntegerField(unique=True, verbose_name="회차")
    draw_date = models.DateTimeField(auto_now_add=True, verbose_name="추첨 일시")
    
    # 당첨 번호 6개와 보너스 번호를 저장 (추첨 전에는 Null 허용)
    # 콤마(,)로 구분된 문자열로 저장합니다 (예: "3,11,14,22,30,41")
    winning_numbers = models.CharField(max_length=30, blank=True, null=True, verbose_name="당첨 번호")
    bonus_number = models.PositiveIntegerField(blank=True, null=True, verbose_name="보너스 번호")
    is_drawn = models.BooleanField(default=False, verbose_name="추첨 완료 여부")

    def __str__(self):
        return f"제 {self.round_number}회"


class LottoTicket(models.Model):
    """사용자가 구매한 복권 내역"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="구매자")
    round = models.ForeignKey(LottoRound, on_delete=models.CASCADE, verbose_name="회차")
    
    # 사용자가 선택했거나 자동 생성된 번호 6개 (예: "5,12,23,25,38,45")
    numbers = models.CharField(max_length=30, verbose_name="선택 번호")
    is_auto = models.BooleanField(default=False, verbose_name="자동 생성 여부")
    purchase_date = models.DateTimeField(auto_now_add=True, verbose_name="구매 일시")
    
    # 당첨 등수 (추첨 전: null / 낙첨: 0 / 1~5등)
    rank = models.IntegerField(blank=True, null=True, verbose_name="당첨 등수")

    def __str__(self):
        return f"{self.user.username} - {self.round} ({self.numbers})"