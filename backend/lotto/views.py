# backend/lotto/views.py
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import LottoRound, LottoTicket

def index(request):
    """메인 페이지: 현재 진행 중인 회차 정보 표시"""
    current_round = LottoRound.objects.order_by('-round_number').first()
    if not current_round:
        current_round = LottoRound.objects.create(round_number=1)
        
    return render(request, 'lotto/index.html', {'current_round': current_round})

@login_required
def buy_ticket(request):
    """복권 구매 처리 (POST 요청)"""
    if request.method == "POST":
        current_round = LottoRound.objects.order_by('-round_number').first()
        
        if current_round.is_drawn:
            messages.error(request, "현재 회차는 이미 추첨이 마감되었습니다.")
            return redirect('lotto:index')
            
        is_auto = request.POST.get('is_auto') == 'true'
        
        if is_auto:
            auto_numbers = sorted(random.sample(range(1, 46), 6))
            numbers_str = ",".join(map(str, auto_numbers))
        else:
            selected_numbers = request.POST.getlist('numbers')
            
            if len(selected_numbers) != 6:
                messages.error(request, "정확히 6개의 숫자를 선택해야 합니다.")
                return redirect('lotto:index')
                
            try:
                int_numbers = sorted([int(n) for n in selected_numbers])
                if any(n < 1 or n > 45 for n in int_numbers) or len(set(int_numbers)) != 6:
                    raise ValueError
                numbers_str = ",".join(map(str, int_numbers))
            except ValueError:
                messages.error(request, "올바르지 않은 번호가 포함되어 있습니다.")
                return redirect('lotto:index')

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

def signup(request):
    """일반 사용자 회원가입"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "회원가입 및 로그인이 완료되었습니다!")
            return redirect('lotto:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

    # backend/lotto/views.py 맨 아래에 추가

@login_required
def admin_dashboard(request):
    """관리자 대시보드: 판매 내역 확인 및 추첨 기능 제공"""
    # 슈퍼유저(관리자)가 아니면 접근 차단
    if not request.user.is_staff:
        messages.error(request, "관리자 권한이 필요합니다.")
        return redirect('lotto:index')
        
    current_round = LottoRound.objects.order_by('-round_number').first()
    all_tickets = LottoTicket.objects.filter(round=current_round).order_by('-purchase_date')
    past_rounds = LottoRound.objects.filter(is_drawn=True).order_by('-round_number')
    
    context = {
        'current_round': current_round,
        'all_tickets': all_tickets,
        'past_rounds': past_rounds,
    }
    return render(request, 'lotto/admin_dashboard.html', context)

@login_required
def draw_lotto(request):
    """관리자 추첨 실행 및 등수 판정 알고리즘"""
    if not request.user.is_staff:
        messages.error(request, "관리자 권한이 필요합니다.")
        return redirect('lotto:index')

    if request.method == "POST":
        current_round = LottoRound.objects.order_by('-round_number').first()
        
        if current_round.is_drawn:
            messages.error(request, "이미 추첨이 완료된 회차입니다.")
            return redirect('lotto:admin_dashboard')
            
        # 1. 당첨 번호 6개 및 보너스 번호 생성 (중복 없는 7개 추출)
        draw_pool = random.sample(range(1, 46), 7)
        winning_numbers = sorted(draw_pool[:6])
        bonus_number = draw_pool[6]
        
        # 2. 현재 회차 정보 업데이트
        current_round.winning_numbers = ",".join(map(str, winning_numbers))
        current_round.bonus_number = bonus_number
        current_round.is_drawn = True
        current_round.save()
        
        # 3. 당해 회차에 판매된 모든 티켓 당첨 판정 (Set 교집합 연산)
        tickets = LottoTicket.objects.filter(round=current_round)
        winning_set = set(winning_numbers)
        
        for ticket in tickets:
            # 문자열로 저장된 티켓 번호를 정수 집합(Set)으로 변환
            ticket_set = set(map(int, ticket.numbers.split(',')))
            
            # 맞춘 숫자의 개수 계산 (교집합 크기)
            match_count = len(ticket_set.intersection(winning_set))
            
            # 등수 판정 기준 적용
            if match_count == 6:
                ticket.rank = 1
            elif match_count == 5 and bonus_number in ticket_set:
                ticket.rank = 2
            elif match_count == 5:
                ticket.rank = 3
            elif match_count == 4:
                ticket.rank = 4
            elif match_count == 3:
                ticket.rank = 5
            else:
                ticket.rank = 0  # 낙첨
                
            ticket.save()
            
        # 4. 다음 회차 자동으로 미리 생성해두기
        LottoRound.objects.create(round_number=current_round.round_number + 1)
        
        messages.success(
            request, 
            f"제 {current_round.round_number}회 추첨이 완료되었습니다! "
            f"당첨번호: {current_round.winning_numbers} + 보너스: {bonus_number}"
        )
        
    return redirect('lotto:admin_dashboard')