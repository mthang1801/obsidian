```mermaid
---

title: "Pattern 2 — Saga Compensation Flow (Advanced)"

---

flowchart TB

CreateOrder([Order Created])

subgraph Forward["`✅ Forward Path <br>(Saga Steps)`"]

direction TB

ReserveInventory[Reserve Inventory] --> |success|Payment[Charge Payment]

Payment --> |success| Confirm["`Confirm<br> Shipment`"]

Confirm --> |success| Notify[Notify Customer]

Confirm --> |success| Shipment

end

  

subgraph Compensate[Compensate Path]

direction TB

CancelShipment["`Cancel <br> Shipment`"] --> RefundPayment["`Refund <br> Payment`"]

RefundPayment --> ReleaseInventory["`Release<br> Inventory`"]

end

  

ReserveInventory --> |failed| SagaFailedNoRollbackNeeded(["`Saga Failed <br> — no rollback needed`"])

Payment --x SagaFailedNoRollbackNeeded

CreateOrder ==> ReserveInventory

Payment --> |payment failed| ReleaseInventory

Confirm --> |confirm failed| RefundPayment

RefundPayment --> OrderCancelled([Order Cancelled])

Shipment --> |shipment failed| CancelShipment
```

**Expert insight:**

- `==>` (thick) cho forward/happy path — scan nhanh ngay critical path
- `-->` (normal) cho failure branches — secondary
- `--x` (cross) đánh dấu đường bị terminate/blocked
- Compensation steps đi **ngược chiều**: `S3 fails → C3 → C2 → C1` — pattern này phải rõ trong diagram
- Không bao giờ vẽ compensation bằng `-->` thường — người đọc sẽ nhầm với forward path