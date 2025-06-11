from app.config import settings


def calculate_metrics(trades):
    """Calculate risk metrics for a set of trades"""
    if not trades:
        return {}

    # 1. Win Ratio
    winning_trades = [t for t in trades if t.profit > 0]
    win_ratio = len(winning_trades) / len(trades) if trades else 0

    # 2. Profit Factor
    total_profit = sum(t.profit for t in winning_trades)
    total_loss = abs(sum(t.profit for t in trades if t.profit < 0))
    profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')

    # 3. Max Drawdown
    balance = settings.INITIAL_BALANCE
    peak = balance
    max_drawdown = 0
    for trade in sorted(trades, key=lambda t: t.closed_at):
        balance += trade.profit
        if balance > peak:
            peak = balance
        drawdown = (peak - balance) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    # 4. Stop Loss Used
    stop_loss_used = len([t for t in trades if t.price_sl is not None]) / len(trades)

    # 5. Take Profit Used Percentage (NEW)
    take_profit_used = len([t for t in trades if t.price_tp is not None]) / len(trades) if trades else 0

    # 6. HFT Detection
    hft_count = 0
    for trade in trades:
        duration = trade.closed_at - trade.opened_at
        if duration.total_seconds() < settings.HFT_DURATION:
            hft_count += 1

    # 7. Layering Detection
    events = []
    for trade in trades:
        events.append((trade.opened_at, 1))   # Trade open
        events.append((trade.closed_at, -1))  # Trade close

    events.sort(key=lambda x: x[0])
    current_open = 0
    max_open = 0
    for _, change in events:
        current_open += change
        if current_open > max_open:
            max_open = current_open

    last_trade = max(t.closed_at for t in trades) if trades else None

    return {
        'win_ratio': win_ratio,
        'profit_factor': profit_factor,
        'max_drawdown': max_drawdown,
        'stop_loss_used': stop_loss_used,
        'take_profit_used': take_profit_used,
        'hft_count': hft_count,
        'max_layering': max_open,
        'last_trade_at': last_trade
    }


def calculate_risk_score(metrics):
    """Calculate risk score from metrics"""
    # Simple weighted average
    weights = {
        'win_ratio': 0.15,
        'profit_factor': 0.15,
        'max_drawdown': 0.20,
        'stop_loss_used': 0.15,
        'take_profit_used': 0.15,
        'hft_count': 0.15,
        'max_layering': 0.20
    }

    # Normalize metrics to 0-100 scale
    normalized = {
        'win_ratio': min(metrics['win_ratio'] * 100, 100),
        'profit_factor': min(metrics['profit_factor'] * 10, 100) if metrics['profit_factor'] != float('inf') else 100,
        'max_drawdown': metrics['max_drawdown'] * 100,
        'stop_loss_used': metrics['stop_loss_used'] * 100,
        'take_profit_used': metrics['take_profit_used'] * 100,
        'hft_count': min(metrics['hft_count'] * 10, 100),
        'max_layering': min(metrics['max_layering'] * 20, 100)
    }

    # Calculate weighted score
    score = sum(normalized[k] * weights[k] for k in weights)
    return min(score, 100)


def generate_risk_signals(metrics):
    """Generate risk signals based on thresholds"""
    signals = []

    if metrics['win_ratio'] < settings.WIN_RATIO_THRESHOLD:
        signals.append("low_win_ratio")
    if metrics['max_drawdown'] > settings.DRAWDOWN_THRESHOLD:
        signals.append("high_drawdown")
    if metrics['hft_count'] > 0:
        signals.append("hft_signal")
    if metrics['stop_loss_used'] < settings.STOP_LOSS_THRESHOLD:
        signals.append("low_stop_loss_usage")
    if metrics['take_profit_used'] < settings.TAKE_PROFIT_THRESHOLD:
        signals.append("low_take_profit_usage")

    return signals
