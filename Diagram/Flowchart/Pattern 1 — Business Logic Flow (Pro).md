```mermaid
flowchart TB

subgraph input [📥 Input Layer]

direction TB

Request([Http Request]) --> AuthValidate{JWT valid?}

AuthValidate --> |valid| RateLimit{Ralimit Ok?}

end

  

subgraph validate [🔍 Validation Layer]

SchemaValidate{SchemaValid?} --> |Yes| IdempotencyKeyValidate{IdempotencyKey exists?}

IdempotencyKeyValidate --> |New| BusinessValidate{Business rules?}

end

  

subgraph processing [⚙️ Processing Layer]

P1[Acquire\ndistributed lock] --> P2["`Execute <br> usecase`"]

P2 --> P3[Publish domain event]

P2 --> P4@{ shape: text, label: "DB Error", fill: #red}

end

  

subgraph output [📤 Output Layer]

ReturnInvalid([40x,50x])

ReturnSuccess([20x])

InvalidateCache[Invalidate cache]

end

  

AuthValidate --> |invalid| ReturnInvalid

RateLimit --> |Ok| SchemaValidate

RateLimit --> |Exceed 429| ReturnInvalid

SchemaValidate --> |invalid 400| ReturnInvalid

BusinessValidate --> |Pass| P1

BusinessValidate --> |Fail 422| ReturnInvalid

IdempotencyKeyValidate --> |Duplicate| ReturnSuccess

P4 --> |Internal 500| ReturnInvalid

P3 -->InvalidateCache
```

**Điểm cần chú ý:**

- `ERR` node dùng chung cho nhiều nhánh lỗi — tránh vẽ 5 ERR node giống nhau
- Label trên edge phải nói rõ HTTP status code khi có thể: `429`, `400`, `422`
- `IDEMPOT` check trước `BIZ` rule — đây là thứ tự quan trọng về performance (fail fast)
- Subgraph name viết theo RESPONSIBILITY, không phải tech: `"Validation Layer"` không phải `"Middleware"`