// 更新滑块值显示
function updateValue(value, elementId) {
    document.getElementById(elementId).textContent = value;
}

// 更新指标显示
function updateMetrics(accuracy, precision, recall, f1_score) {
    // 获取之前的值
    const prevAccuracy = parseFloat(document.getElementById('accuracy').style.width) || 0;
    const prevPrecision = parseFloat(document.getElementById('precision').style.width) || 0;
    const prevRecall = parseFloat(document.getElementById('recall').style.width) || 0;
    const prevF1Score = parseFloat(document.getElementById('f1-score').style.width) || 0;

    // 更新准确率
    document.getElementById('accuracy').style.width = accuracy + '%';
    document.getElementById('accuracy').textContent = accuracy + '%';
    toggleTrendIndicator('accuracy', accuracy, prevAccuracy);

    // 更新精确率
    document.getElementById('precision').style.width = precision + '%';
    document.getElementById('precision').textContent = precision + '%';
    toggleTrendIndicator('precision', precision, prevPrecision);

    // 更新召回率
    document.getElementById('recall').style.width = recall + '%';
    document.getElementById('recall').textContent = recall + '%';
    toggleTrendIndicator('recall', recall, prevRecall);

    // 更新F1分数
    document.getElementById('f1-score').style.width = f1_score + '%';
    document.getElementById('f1-score').textContent = f1_score + '%';
    toggleTrendIndicator('f1-score', f1_score, prevF1Score);
}

// 切换趋势指示器
function toggleTrendIndicator(metric, currentValue, previousValue) {
    const upArrow = document.getElementById(`i-${metric}-up`);
    const downArrow = document.getElementById(`i-${metric}-down`);

    if (currentValue > previousValue) {
        upArrow.style.display = 'inline-block';
        downArrow.style.display = 'none';
    } else if (currentValue < previousValue) {
        upArrow.style.display = 'none';
        downArrow.style.display = 'inline-block';
    } else {
        upArrow.style.display = 'none';
        downArrow.style.display = 'none';
    }
}

// 提交表单处理
document.getElementById('submitButton').addEventListener('click', function() {
    // 显示加载动画
    document.getElementById('loading').style.display = 'inline-block';
    this.disabled = true;

    // 获取表单数据
    const formData = {
        lr: document.querySelector('input[name="lr"]').value,
        wd: document.querySelector('input[name="wd"]').value,
        batch_size: document.querySelector('input[name="batch_size"]').value,
        num_epochs: document.querySelector('input[name="num_epochs"]').value,
    };

    // 发送AJAX请求
    fetch('/tuning_cnn_lstm_att_duofenlei/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 更新指标显示
            updateMetrics(
                parseFloat(data.accuracy),
                parseFloat(data.precision1),
                parseFloat(data.recall),
                parseFloat(data.f1)
            );
        } else {
            alert('训练过程中出现错误：' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('发生错误：' + error);
    })
    .finally(() => {
        // 隐藏加载动画并启用按钮
        document.getElementById('loading').style.display = 'none';
        document.getElementById('submitButton').disabled = false;
    });
}); 