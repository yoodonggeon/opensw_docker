# backend/lotto/views.py
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LottoRound, LottoTicket

def index(request):
    """메인 페이지: 현재 진행 중인 회차 정보 표시"""
    # 가장 최근 회차를 가져오거나, 없으면 1회차를 기본으로 생성
    current_round = LottoRound.objects.order_by('-round_number').first()
    if not current_round:
        current_round = LottoRound.objects.create(round_number=1)
        
    return render(request, 'lotto/index.html', {'current_round': current_round})

@login_required
def buy_ticket(request):
    """복권 구매 처리 (POST 요청)"""
    if request.method == "POST":
        current_round = LottoRound.objects.order_by('-round_number').first()
        
        # 이미 추첨이 완료된 회차라면 구매 불가
        if current_round.is_drawn:
            messages.error(request, "현재 회차는 이미 추첨이 마감되었습니다.")
            return redirect('lotto:index')
            
        is_auto = request.POST.get('is_auto') == 'true'
        
        if is_auto:
            # [자동 생성] 1~45 중 중복 없이 6개 번호 추출 후 오름차순 정렬
            auto_numbers = sorted(random.sample(range(1, 46), 6))
            # DB에 저장하기 좋게 콤마로 연결된 문자열 변환 (예: "5,12,23,34,40,41")
            numbers_str = ",".join(map(str, auto_numbers))
        else:
            # [수동 생성] 프론트엔드에서 보낸 6개 숫자 받기
            selected_numbers = request.POST.getlist('numbers')
            
            # 유효성 검사: 정확히 6개인지, 숫자가 올바른지 확인
            if len(selected_numbers) != 6:
                messages.error(request, "정확히 6개의 숫자를 선택해야 합니다.")
                return redirect('lotto:index')
                
            try:
                # 숫자로 변환 후 오름차순 정렬
                int_numbers = sorted([int(n) for n in selected_numbers])
                # 1~45 범위를 벗어나거나 중복이 있는지 체크
                if any(n < 1 or n > 45 for n in int_numbers) or len(set(int_numbers)) != 6:
                    raise ValueError
                numbers_str = ",".join(map(str, int_numbers))
            except ValueError:
                messages.error(request, "올바르지 않은 번호가 포함되어 있습니다.")
                return redirect('lotto:index')

        # 티켓 저장
        LottoTicket.objects.create(
            user=request.user,
            round=current_round,
            numbers=numbers_str,
            is_auto=is_auto
        )
        
        type_str = "자동" if is_auto else "수동"
        messages.success(request, f"로또 {type_str} 구매가 완료되었습니다! 번호: {numbers_str}")
        return redirect('lotto:my_tickets')
        
    return redirect('lotto:index')

@login_required
def my_tickets(request):
    """사용자가 구매한 복권 목록 조회"""
    tickets = LottoTicket.objects.filter(user=request.user).order_by('-purchase_date')
    return render(request, 'lotto/my_tickets.html', {'tickets': tickets})