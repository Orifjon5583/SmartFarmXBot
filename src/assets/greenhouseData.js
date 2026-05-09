export const sensorSnapshot = {
  temperature: 27.4,
  humidity: 68,
  soilMoisture: 47,
  light: 735,
  weather: {
    condition: 'Ochiq va barqaror ob-havo',
    outsideTemp: 22,
    wind: 8,
    uv: 5,
  },
};

export const historySeries = Array.from({ length: 24 }, (_, index) => {
  const hour = `${String(index).padStart(2, '0')}:00`;
  return {
    time: hour,
    temperature: Math.round((23 + Math.sin(index / 3) * 3 + index * 0.11) * 10) / 10,
    humidity: Math.round(62 + Math.cos(index / 4) * 8),
    soil: Math.round(52 - index * 0.42 + Math.sin(index / 2) * 4),
    light: Math.max(110, Math.round(420 + Math.sin((index - 6) / 5) * 360)),
    energy: Math.round(1.8 + Math.sin(index / 4) * 0.5 + index * 0.045),
  };
});

export const activityLogs = [
  { time: '14:38', device: 'Ventilyator', event: 'Avto rejim yoqildi', value: 'Harorat 31.2C' },
  { time: '13:50', device: 'Nasos', event: 'Sugorish sikli tugadi', value: '18 soniya' },
  { time: '12:24', device: 'Chiroq', event: 'Yoritish darajasi sozlandi', value: '72%' },
  { time: '09:12', device: 'Kamera', event: 'Rasm saqlandi', value: 'Soglom' },
];

export const gpioPins = [
  { pin: 4, label: 'Ventilyator relesi', active: true },
  { pin: 17, label: 'Nasos relesi', active: false },
  { pin: 22, label: 'O‘stirish chirog‘i', active: true },
  { pin: 27, label: 'Kamera', active: true },
  { pin: 5, label: 'DHT22', active: true },
  { pin: 6, label: 'Tuproq ADC', active: true },
  { pin: 13, label: 'LDR', active: true },
  { pin: 19, label: 'Zaxira', active: false },
];

export const alerts = [
  { id: 1, type: 'warning', title: 'Tuproq namligi chegaraga yaqin', detail: 'B zonada namlik 35 daqiqadan beri pasaymoqda.' },
  { id: 2, type: 'info', title: 'Avtomatika barqaror', detail: 'Ventilyator va yoritish qoidalari normal ishlayapti.' },
  { id: 3, type: 'success', title: 'O‘simlik salomatligi tekshirildi', detail: 'Oxirgi kadrda xloroz belgilari aniqlanmadi.' },
];
