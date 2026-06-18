document.addEventListener('DOMContentLoaded', () => {
    // Set default dates
    const endDateInput = document.getElementById('end-date');
    const startDateInput = document.getElementById('start-date');
    
    const today = new Date();
    const pastYear = new Date(today);
    pastYear.setFullYear(today.getFullYear() - 2);

    endDateInput.value = today.toISOString().split('T')[0];
    startDateInput.value = pastYear.toISOString().split('T')[0];

    const tickerInput = document.getElementById('ticker');
    const suggestionsContainer = document.getElementById('suggestions-container');

    // Autocomplete Logic
    let debounceTimer;
    tickerInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        
        if (query.length < 1) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    suggestionsContainer.innerHTML = '';
                    data.results.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'suggestion-item';
                        div.innerHTML = `
                            <span class="suggestion-symbol">${item.symbol}</span>
                            <span class="suggestion-name">${item.name}</span>
                        `;
                        div.addEventListener('click', () => {
                            tickerInput.value = item.symbol;
                            suggestionsContainer.style.display = 'none';
                        });
                        suggestionsContainer.appendChild(div);
                    });
                    suggestionsContainer.style.display = 'block';
                } else {
                    suggestionsContainer.style.display = 'none';
                }
            } catch (err) {
                console.error("Failed to fetch suggestions", err);
            }
        }, 300); // 300ms debounce
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!tickerInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });

    const form = document.getElementById('prediction-form');
    const loader = document.getElementById('loader');
    const resultContent = document.getElementById('result-content');
    const errorContent = document.getElementById('error-content');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Hide old results
        resultContent.style.display = 'none';
        errorContent.style.display = 'none';
        
        // Show loader
        loader.style.display = 'flex';

        const ticker = document.getElementById('ticker').value.toUpperCase();
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ticker: ticker,
                    start_date: startDate,
                    end_date: endDate
                })
            });

            const data = await response.json();

            // Hide loader
            loader.style.display = 'none';

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch prediction.');
            }

            // Update UI
            document.getElementById('result-ticker').innerText = data.ticker;
            
            const predValue = document.getElementById('prediction-value');
            const predIcon = document.getElementById('prediction-icon');
            
            predValue.innerText = data.prediction;
            if (data.prediction === 'UP') {
                predValue.className = 'prediction-value up';
                predIcon.innerText = '🟢 📈';
            } else {
                predValue.className = 'prediction-value down';
                predIcon.innerText = '🔴 📉';
            }

            document.getElementById('confidence-value').innerText = data.confidence + '%';
            document.getElementById('accuracy-value').innerText = data.accuracy + '%';

            // Draw Chart
            if (data.chart_data && data.chart_data.dates) {
                const trace = {
                    x: data.chart_data.dates,
                    close: data.chart_data.close,
                    high: data.chart_data.high,
                    low: data.chart_data.low,
                    open: data.chart_data.open,
                    increasing: {line: {color: '#10b981'}},
                    decreasing: {line: {color: '#ef4444'}},
                    type: 'candlestick',
                    xaxis: 'x',
                    yaxis: 'y'
                };

                const layout = {
                    margin: { t: 10, l: 40, r: 10, b: 30 },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    xaxis: {
                        rangeslider: { visible: false },
                        color: '#9ca3af',
                        gridcolor: 'rgba(255,255,255,0.1)'
                    },
                    yaxis: {
                        color: '#9ca3af',
                        gridcolor: 'rgba(255,255,255,0.1)'
                    },
                    font: {
                        family: 'Inter, sans-serif'
                    }
                };

                Plotly.newPlot('chart-container', [trace], layout, {responsive: true});
            }

            // Show result
            resultContent.style.display = 'block';

        } catch (error) {
            loader.style.display = 'none';
            document.getElementById('error-message').innerText = error.message;
            errorContent.style.display = 'block';
        }
    });
});
