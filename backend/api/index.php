<?php
/**
 * NextentCreator - API Gateway
 * PHP API网关 - 请求路由、会话管理、与Python Agent通信
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// 配置
$config = [
    'python_api_url' => 'http://localhost:8000',  // Python FastAPI服务地址
    'version' => '1.0.0',
    'name' => 'NextentCreator API'
];

// 路由处理
$request_uri = $_SERVER['REQUEST_URI'];
$request_method = $_SERVER['REQUEST_METHOD'];
$input = json_decode(file_get_contents('php://input'), true);

// API路由
$routes = [
    'GET /' => 'apiInfo',
    'GET /api' => 'apiInfo',
    'GET /api/agents' => 'listAgents',
    'POST /api/create' => 'createContent',
    'GET /api/status/{id}' => 'getStatus',
    'POST /api/feedback' => 'submitFeedback',
];

// 路由匹配
$matched = false;
foreach ($routes as $route => $handler) {
    list($method, $path) = explode(' ', $route);
    
    // 处理路径参数
    $pattern = preg_replace('/\{([^}]+)\}/', '([^/]+)', $path);
    $pattern = '#^' . $pattern . '$#';
    
    if ($request_method === $method && preg_match($pattern, $request_uri, $matches)) {
        array_shift($matches); // 移除完整匹配
        $matched = true;
        call_user_func_array($handler, array_merge([$input], $matches));
        break;
    }
}

if (!$matched) {
    http_response_code(404);
    echo json_encode(['error' => 'Not Found', 'path' => $request_uri]);
}

// ==================== 处理器函数 ====================

/**
 * API信息
 */
function apiInfo($input) {
    global $config;
    echo json_encode([
        'name' => $config['name'],
        'version' => $config['version'],
        'status' => 'running',
        'agents' => [
            ['id' => 'intent', 'name' => '意图识别Agent', 'status' => 'online'],
            ['id' => 'dispatcher', 'name' => '任务分发Agent', 'status' => 'online'],
            ['id' => 'article', 'name' => '图文创作Agent', 'status' => 'online'],
            ['id' => 'tech', 'name' => '技术创作Agent', 'status' => 'online'],
            ['id' => 'social', 'name' => '社交创作Agent', 'status' => 'online'],
            ['id' => 'polish', 'name' => '润色优化Agent', 'status' => 'online'],
        ],
        'endpoints' => [
            ['method' => 'GET', 'path' => '/api', 'description' => 'API信息'],
            ['method' => 'GET', 'path' => '/api/agents', 'description' => '获取Agent列表'],
            ['method' => 'POST', 'path' => '/api/create', 'description' => '创建内容'],
            ['method' => 'GET', 'path' => '/api/status/{id}', 'description' => '查询任务状态'],
            ['method' => 'POST', 'path' => '/api/feedback', 'description' => '提交反馈'],
        ]
    ]);
}

/**
 * 获取Agent列表
 */
function listAgents($input) {
    $agents = [
        [
            'id' => 'intent',
            'name' => '意图识别Agent',
            'description' => '解析用户需求，确定内容类型和创作方向',
            'icon' => '🎯',
            'status' => 'online',
            'capabilities' => ['需求解析', '类型识别', '参数提取']
        ],
        [
            'id' => 'dispatcher',
            'name' => '任务分发Agent',
            'description' => '根据意图识别结果，分发到对应专项Agent',
            'icon' => '📡',
            'status' => 'online',
            'capabilities' => ['任务路由', '负载均衡', '异常处理']
        ],
        [
            'id' => 'article',
            'name' => '图文创作Agent',
            'description' => '长图文内容创作，支持公众号、知乎、博客等',
            'icon' => '📝',
            'status' => 'online',
            'capabilities' => ['文章生成', '大纲设计', '排版优化']
        ],
        [
            'id' => 'tech',
            'name' => '技术创作Agent',
            'description' => '技术文档和教程创作，包含代码示例',
            'icon' => '💻',
            'status' => 'online',
            'capabilities' => ['技术写作', '代码生成', '步骤说明']
        ],
        [
            'id' => 'social',
            'name' => '社交创作Agent',
            'description' => '短内容和社交帖子创作，适配多平台',
            'icon' => '📱',
            'status' => 'online',
            'capabilities' => ['短文案', '标签优化', '多版本生成']
        ],
        [
            'id' => 'polish',
            'name' => '润色优化Agent',
            'description' => '统一质量把关和风格优化',
            'icon' => '✨',
            'status' => 'online',
            'capabilities' => ['质量检查', '风格统一', 'SEO优化']
        ],
    ];
    
    echo json_encode(['agents' => $agents]);
}

/**
 * 创建内容 - 核心API
 */
function createContent($input) {
    // 验证输入
    if (empty($input['topic'])) {
        http_response_code(400);
        echo json_encode(['error' => '缺少创作主题']);
        return;
    }
    
    $type = $input['type'] ?? 'article';
    $topic = $input['topic'];
    $options = $input['options'] ?? [];
    
    // 生成任务ID
    $taskId = uniqid('task_');
    
    // 记录任务日志
    logTask($taskId, 'started', ['type' => $type, 'topic' => $topic]);
    
    // 调用Python Agent服务
    $result = callPythonAgent($type, $topic, $options);
    
    if ($result['success']) {
        logTask($taskId, 'completed', $result);
        echo json_encode([
            'success' => true,
            'task_id' => $taskId,
            'content' => $result['content'],
            'metadata' => [
                'type' => $type,
                'word_count' => str_word_count($result['content']),
                'created_at' => date('Y-m-d H:i:s'),
                'agents_involved' => $result['agents']
            ]
        ]);
    } else {
        logTask($taskId, 'failed', $result);
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'error' => $result['error'] ?? '创作失败'
        ]);
    }
}

/**
 * 获取任务状态
 */
function getStatus($input, $taskId) {
    $status = getTaskStatus($taskId);
    
    if ($status) {
        echo json_encode([
            'task_id' => $taskId,
            'status' => $status['status'],
            'created_at' => $status['created_at'],
            'updated_at' => $status['updated_at'] ?? null
        ]);
    } else {
        http_response_code(404);
        echo json_encode(['error' => '任务不存在']);
    }
}

/**
 * 提交反馈
 */
function submitFeedback($input) {
    if (empty($input['task_id']) || empty($input['rating'])) {
        http_response_code(400);
        echo json_encode(['error' => '缺少必要参数']);
        return;
    }
    
    // 保存反馈
    saveFeedback($input['task_id'], $input['rating'], $input['comment'] ?? '');
    
    echo json_encode([
        'success' => true,
        'message' => '反馈已提交，感谢你的支持！'
    ]);
}

// ==================== 辅助函数 ====================

/**
 * 调用Python Agent服务
 */
function callPythonAgent($type, $topic, $options) {
    global $config;
    
    // 构建请求数据
    $data = [
        'type' => $type,
        'topic' => $topic,
        'options' => $options
    ];
    
    // 使用cURL调用Python服务
    $ch = curl_init($config['python_api_url'] . '/create');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_TIMEOUT, 120); // 2分钟超时
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200 && $response) {
        return json_decode($response, true);
    }
    
    // 如果Python服务不可用，返回模拟数据（用于演示）
    return generateMockContent($type, $topic);
}

/**
 * 生成模拟内容（演示用）
 */
function generateMockContent($type, $topic) {
    $agents = [];
    $content = '';
    
    // 模拟Agent协作流程
    $agents[] = ['name' => '意图识别Agent', 'action' => '解析需求', 'time' => '0.5s'];
    $agents[] = ['name' => '任务分发Agent', 'action' => '分发任务', 'time' => '0.3s'];
    
    if ($type === 'article') {
        $agents[] = ['name' => '图文创作Agent', 'action' => '生成文章', 'time' => '3.2s'];
        $content = generateArticleContent($topic);
    } elseif ($type === 'tech') {
        $agents[] = ['name' => '技术创作Agent', 'action' => '生成文档', 'time' => '2.8s'];
        $content = generateTechContent($topic);
    } else {
        $agents[] = ['name' => '社交创作Agent', 'action' => '生成文案', 'time' => '1.5s'];
        $content = generateSocialContent($topic);
    }
    
    $agents[] = ['name' => '润色优化Agent', 'action' => '质量优化', 'time' => '1.2s'];
    
    return [
        'success' => true,
        'content' => $content,
        'agents' => $agents
    ];
}

/**
 * 生成文章类内容
 */
function generateArticleContent($topic) {
    return <<<EOT
# {$topic}：从入门到精通的完整指南

在这个信息爆炸的时代，掌握{$topic}已经成为必备技能。本文将带你从零开始，系统性地学习核心概念和实践方法。

## 一、为什么学习{$topic}？

{$topic}不仅能提升你的工作效率，还能为你打开新的职业机会。根据最新调查，掌握这项技能的专业人士平均薪资比同行高出30%。

### 主要优势：
- **效率提升**：自动化处理重复性任务
- **竞争力增强**：在职场中脱颖而出
- **创新机会**：开拓新的业务领域

## 二、核心概念解析

要真正理解{$topic}，我们需要从基础概念开始：

### 1. 基础原理
{$topic}的核心在于理解其底层机制和工作流程。只有掌握了这些基础，才能在实际应用中灵活运用。

### 2. 常见应用场景
- 企业级应用开发
- 数据分析和可视化
- 自动化流程设计

### 3. 最佳实践
遵循行业标准和最佳实践，可以避免常见的陷阱和错误。

## 三、实战案例分享

理论结合实践才能真正掌握。以下是三个经典案例：

### 案例一：初学者入门
适合零基础的学习路径，循序渐进掌握核心技能。

### 案例二：进阶提升
针对有一定基础的开发者，深入探讨高级特性和优化技巧。

### 案例三：企业级应用
展示如何在实际项目中应用{$topic}解决复杂问题。

## 四、总结与展望

通过本文的学习，相信你已经对{$topic}有了全面的认识。记住，持续学习和实践是掌握任何技能的关键。

未来，{$topic}将继续演进，带来更多可能性和机遇。保持好奇心，持续探索，你一定能在这个领域取得成功！

---

*本文由 NextentCreator AI 自动生成*
EOT;
}

/**
 * 生成技术类内容
 */
function generateTechContent($topic) {
    $className = str_replace(' ', '', $topic);
    return <<<EOT
# {$topic}技术详解

本文深入剖析{$topic}的技术原理，包含完整代码示例和最佳实践。

## 概述

{$topic}是现代软件开发中的重要技术，它解决了传统方案中的多个痛点：

- 性能瓶颈问题
- 可扩展性挑战
- 维护成本高

## 核心代码示例

### 基础用法

```php
<?php
/**
 * {$className} 核心类
 */
class {$className}Engine 
{
    private \$config;
    private \$initialized = false;
    
    public function __construct(array \$config = []) 
    {
        \$this->config = array_merge([
            'mode' => 'production',
            'debug' => false,
            'timeout' => 30
        ], \$config);
    }
    
    /**
     * 初始化引擎
     */
    public function init(): bool 
    {
        if (\$this->initialized) {
            return true;
        }
        
        // 初始化逻辑
        \$this->initialized = true;
        return true;
    }
    
    /**
     * 执行核心操作
     */
    public function execute(\$input) 
    {
        if (!\$this->initialized) {
            throw new RuntimeException('引擎未初始化');
        }
        
        // 核心处理逻辑
        return \$this->process(\$input);
    }
    
    private function process(\$input) 
    {
        // 实际处理逻辑
        return \$input;
    }
}

// 使用示例
\$engine = new {$className}Engine([
    'mode' => 'development',
    'debug' => true
]);

\$engine->init();
\$result = \$engine->execute(\$data);
```

## 实现步骤

### 1. 环境准备

```bash
# 安装依赖
composer require vendor/{$topic}-sdk

# 配置环境变量
cp .env.example .env
```

### 2. 核心配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| mode | string | production | 运行模式 |
| debug | bool | false | 调试模式 |
| timeout | int | 30 | 超时时间 |

### 3. API接口

#### 初始化接口
```http
POST /api/v1/{$topic}/init
Content-Type: application/json

{
    "config": {
        "mode": "production"
    }
}
```

#### 执行接口
```http
POST /api/v1/{$topic}/execute
Content-Type: application/json

{
    "input": "your data here"
}
```

## 性能优化

### 1. 缓存策略
- 使用 Redis 缓存热点数据
- 实现本地缓存减少网络请求

### 2. 并发处理
- 使用连接池管理资源
- 异步处理非关键任务

### 3. 监控告警
- 集成 Prometheus 监控
- 设置关键指标告警

## 常见问题

**Q: 如何处理并发请求？**  
A: 建议使用连接池和异步处理机制，参考上面的代码示例。

**Q: 性能瓶颈在哪里？**  
A: 通常是 I/O 操作和数据库查询，建议使用缓存和优化 SQL。

**Q: 如何调试问题？**  
A: 开启 debug 模式，查看详细日志，使用 Xdebug 进行断点调试。

## 总结

{$topic}是一个强大而灵活的技术方案，通过合理的设计和优化，可以显著提升系统性能和开发效率。

---

*本文档由 NextentCreator AI 自动生成*
EOT;
}

/**
 * 生成社交类内容
 */
function generateSocialContent($topic) {
    return <<<EOT
💡 {$topic}心得分享

刚完成了{$topic}的学习，分享几点收获：

🎯 关键点1：找准方向比盲目努力更重要  
在开始学习之前，先明确自己的目标和应用场景，避免走弯路。

💪 关键点2：坚持实践，理论结合实际  
光学理论是不够的，一定要动手实践，在项目中不断总结和优化。

🚀 关键点3：保持好奇心，持续学习  
技术更新很快，要保持学习的热情，跟上行业发展的步伐。

✨ 额外收获：
- 认识了一群志同道合的朋友
- 开阔了技术视野
- 提升了问题解决能力

如果你也在学习{$topic}，欢迎交流讨论！一起进步 💪

#{$topic} #学习笔记 #成长心得 #技术分享
EOT;
}

/**
 * 记录任务日志
 */
function logTask($taskId, $status, $data) {
    $logDir = __DIR__ . '/logs';
    if (!is_dir($logDir)) {
        mkdir($logDir, 0755, true);
    }
    
    $logFile = $logDir . '/tasks.log';
    $logEntry = [
        'task_id' => $taskId,
        'status' => $status,
        'timestamp' => date('Y-m-d H:i:s'),
        'data' => $data
    ];
    
    file_put_contents($logFile, json_encode($logEntry) . "\n", FILE_APPEND);
}

/**
 * 获取任务状态
 */
function getTaskStatus($taskId) {
    // 简化实现，实际应该从数据库或缓存中获取
    return [
        'task_id' => $taskId,
        'status' => 'completed',
        'created_at' => date('Y-m-d H:i:s', strtotime('-5 minutes')),
        'updated_at' => date('Y-m-d H:i:s')
    ];
}

/**
 * 保存反馈
 */
function saveFeedback($taskId, $rating, $comment) {
    $feedbackDir = __DIR__ . '/feedback';
    if (!is_dir($feedbackDir)) {
        mkdir($feedbackDir, 0755, true);
    }
    
    $feedbackFile = $feedbackDir . '/' . date('Y-m-d') . '.json';
    $feedback = [
        'task_id' => $taskId,
        'rating' => $rating,
        'comment' => $comment,
        'timestamp' => date('Y-m-d H:i:s')
    ];
    
    $existing = [];
    if (file_exists($feedbackFile)) {
        $existing = json_decode(file_get_contents($feedbackFile), true) ?: [];
    }
    $existing[] = $feedback;
    
    file_put_contents($feedbackFile, json_encode($existing, JSON_PRETTY_PRINT));
}
