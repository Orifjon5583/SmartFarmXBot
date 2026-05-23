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
  { time: '14:38', device: '2 ta kuler', event: 'Avto rejim yoqildi', value: 'Harorat 31.2C' },
  { time: '13:50', device: "Tomchilatib sug'orish", event: 'Sugorish sikli tugadi', value: '18 soniya' },
  { time: '12:24', device: 'LED chiroq', event: 'Yoritish darajasi sozlandi', value: '72%' },
  { time: '09:12', device: "Yomg'irlatib sug'orish", event: "Qo'l rejimida o'chirildi", value: 'OFF' },
];

export const gpioPins = [
  { pin: 17, label: "Tomchilatib sug'orish relesi", active: false },
  { pin: 27, label: "Yomg'irlatib sug'orish relesi", active: false },
  { pin: 22, label: '2 ta kuler umumiy relesi', active: true },
  { pin: 5, label: 'LED chiroq relesi', active: true },
  { pin: 4, label: 'DHT22 DATA', active: true },
  { pin: 23, label: 'Fotorezistor digital', active: true },
  { pin: 18, label: 'IR receiver', active: true },
  { pin: 8, label: 'MCP3008 CE0', active: true },
];

export const alerts = [
  { id: 1, type: 'warning', title: 'Tuproq namligi chegaraga yaqin', detail: 'B zonada namlik 35 daqiqadan beri pasaymoqda.' },
  { id: 2, type: 'info', title: 'Avtomatika barqaror', detail: 'Kulerlar va yoritish qoidalari normal ishlayapti.' },
  { id: 3, type: 'success', title: "O'simlik salomatligi tekshirildi", detail: 'Oxirgi kadrda xloroz belgilari aniqlanmadi.' },
];
