class IoTDashboard {
    constructor() {
        this.chart = null;
        this.chartData = {
            labels: [],
            datasets: [
                {
                    label: 'Suhu (°C)',
                    data: [],
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'Kelembapan (%)',
                    data: [],
                    borderColor: '#4ecdc4',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'Kecerahan (Lux)',
                    data: [],
                    borderColor: '#ffe66d',
                    backgroundColor: 'rgba(255, 230, 109, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        };
        
        this.init();
    }

    init() {
        this.initChart();
        this.bindEvents();
        this.startDataUpdates();
        this.loadHistory();
        this.loadStatistics();
    }

    initChart() {
        const ctx = document.getElementById('sensorChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: this.chartData,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Data Sensor Real-time'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Waktu'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Suhu (°C) / Kelembapan (%)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Kecerahan (Lux)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                animation: {
                    duration: 750
                }
            }
        });
    }

    bindEvents() {
        // Event listener untuk tombol relay
        document.getElementById('relayOn').addEventListener('click', () => {
            this.controlRelay('ON');
        });

        document.getElementById('relayOff').addEventListener('click', () => {
            this.controlRelay('OFF');
        });

        // Event listener untuk button SEMUA DATA - langsung ke endpoint
        document.getElementById('downloadSemuaData').addEventListener('click', () => {
            this.goToSemuaDataEndpoint();
        });

        // Event listener untuk button STATISTIK DATA - langsung ke endpoint
        document.getElementById('downloadStatistikData').addEventListener('click', () => {
            this.goToStatistikDataEndpoint();
        });
    }

    startDataUpdates() {
        // Update data setiap 2 detik
        setInterval(() => {
            this.fetchLatestData();
        }, 2000);
        
        // Load data pertama kali
        this.fetchLatestData();
        
        // Update statistik setiap 10 detik
        setInterval(() => {
            this.loadStatistics();
        }, 10000);

        // Load history pertama kali
        this.loadHistory();
    }

    async fetchLatestData() {
        try {
            const response = await fetch('/api/sensor/latest');
            const data = await response.json();
            
            this.updateSensorCards(data);
            this.updateChart(data);
            this.updateLastUpdateTime();
            
        } catch (error) {
            console.error('Error fetching latest data:', error);
            this.showError('Gagal mengambil data sensor terbaru');
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/sensor/statistics');
            const stats = await response.json();
            
            if (stats.error) {
                throw new Error(stats.error);
            }
            
            // Update kartu statistik suhu
            document.getElementById('tempMax').textContent = `${stats.temperature.maximum}°C`;
            document.getElementById('tempMin').textContent = `${stats.temperature.minimum}°C`;
            document.getElementById('tempAvg').textContent = `${stats.temperature.average}°C`;
            
        } catch (error) {
            console.error('Error loading statistics:', error);
            // Set default values jika error
            document.getElementById('tempMax').textContent = '--°C';
            document.getElementById('tempMin').textContent = '--°C';
            document.getElementById('tempAvg').textContent = '--°C';
        }
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/sensor/history');
            const data = await response.json();
            
            this.populateHistoryTable(data.slice(0, 50)); // Tampilkan hanya 50 data terbaru di tabel
            
        } catch (error) {
            console.error('Error loading history:', error);
            this.showError('Gagal memuat riwayat data');
        }
    }

    updateSensorCards(data) {
        document.getElementById('temperature').textContent = `${data.suhu.toFixed(1)}°C`;
        document.getElementById('humidity').textContent = `${data.humidity.toFixed(1)}%`;
        document.getElementById('lux').textContent = `${data.lux.toFixed(0)} Lux`;
    }

    updateChart(data) {
        const now = new Date(data.timestamp).toLocaleTimeString();
        
        // Tambah data baru
        this.chartData.labels.push(now);
        this.chartData.datasets[0].data.push(data.suhu);
        this.chartData.datasets[1].data.push(data.humidity);
        this.chartData.datasets[2].data.push(data.lux);
        
        // Batasi jumlah data (maksimal 20 point)
        if (this.chartData.labels.length > 20) {
            this.chartData.labels.shift();
            this.chartData.datasets[0].data.shift();
            this.chartData.datasets[1].data.shift();
            this.chartData.datasets[2].data.shift();
        }
        
        this.chart.update('none');
    }

    async controlRelay(state) {
        try {
            const response = await fetch('/api/relay/control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ state: state })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                document.getElementById('relayStatus').textContent = `Status: ${state}`;
                this.showSuccess(`Relay berhasil di${state === 'ON' ? 'nyalakan' : 'matikan'}`);
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Error controlling relay:', error);
            this.showError('Gagal mengontrol relay');
        }
    }

    populateHistoryTable(data) {
        const tbody = document.querySelector('#historyTable tbody');
        tbody.innerHTML = '';
        
        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleString('id-ID')}</td>
                <td>${row.suhu.toFixed(1)}</td>
                <td>${row.humidity.toFixed(1)}</td>
                <td>${row.lux.toFixed(0)}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Fungsi baru untuk mengarahkan ke endpoint SEMUA DATA
    goToSemuaDataEndpoint() {
        const button = document.getElementById('downloadSemuaData');
        button.textContent = '⏳ Loading...';
        button.disabled = true;
        
        // Buka endpoint di tab baru
        window.open('/api/sensor/history', '_blank');
        
        // Reset button setelah 2 detik
        setTimeout(() => {
            button.textContent = '📥 SEMUA DATA (JSON)';
            button.disabled = false;
        }, 2000);
        
        this.showSuccess('✅ Halaman Semua Data telah dibuka!');
    }

    // Fungsi baru untuk mengarahkan ke endpoint STATISTIK DATA
    goToStatistikDataEndpoint() {
        const button = document.getElementById('downloadStatistikData');
        button.textContent = '⏳ Loading...';
        button.disabled = true;
        
        // Buka endpoint di tab baru
        window.open('/api/sensor/statistik_data', '_blank');
        
        // Reset button setelah 2 detik
        setTimeout(() => {
            button.textContent = '📊 STATISTIK DATA (JSON)';
            button.disabled = false;
        }, 2000);
        
        this.showSuccess('✅ Halaman Statistik Data telah dibuka!');
    }

    updateLastUpdateTime() {
        const now = new Date().toLocaleString('id-ID');
        document.getElementById('lastUpdate').textContent = now;
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Buat elemen notifikasi
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Style notifikasi
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 25px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: 'bold',
            zIndex: '1000',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            backgroundColor: type === 'success' ? '#28a745' : '#dc3545'
        });
        
        document.body.appendChild(notification);
        
        // Hapus notifikasi setelah 3 detik
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Inisialisasi dashboard saat halaman dimuat
document.addEventListener('DOMContentLoaded', () => {
    new IoTDashboard();
});