"""Shared Arrange datasets, defined once from the cahier de test."""


def ct50_dataset(make):
    """Orders of CT-50: PLACED 50.00, PAID 114.00, SHIPPED 20.00, DELIVERED 30.00, CANCELLED 80.00; one product at 4."""
    ana = make.user()
    p40, p50, p20, p30 = (make.product(c, 10) for c in (4_000, 5_000, 2_000, 3_000))
    low = make.product(1_000, 4)
    make.order(ana, [(p50, 1)])  # PLACED 50.00
    make.order(ana, [(p40, 3)], status="PAID")  # 120.00 - 5 % = 114.00
    make.order(ana, [(p20, 1)], status="SHIPPED")  # 20.00
    make.order(ana, [(p30, 1)], status="DELIVERED")  # 30.00
    make.order(ana, [(p40, 2)], status="CANCELLED")  # 80.00, must not count
    return {"p40": p40, "p20": p20, "p30": p30, "low": low}
