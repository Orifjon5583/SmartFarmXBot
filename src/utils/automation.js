export function deriveAutomationState(sensors, thresholds = {}) {
  const temperatureLimit = thresholds.temperature ?? 30;
  const moistureLimit = thresholds.moisture ?? 40;
  const lightLimit = thresholds.light ?? 420;

  return {
    cooler_1: Number(sensors.temperature) > temperatureLimit,
    cooler_2: Number(sensors.temperature) > temperatureLimit + 1,
    drip_pump: Number(sensors.soilMoisture) < moistureLimit,
    rain_pump: Number(sensors.soilMoisture) < moistureLimit - 12,
    photo_led: Number(sensors.light) < lightLimit,
    insect_led: Number(sensors.light) < lightLimit && Number(sensors.gasLevel ?? 0) < 70,
  };
}

export function healthScore(sensors) {
  const temperaturePenalty = Math.abs((sensors.temperature ?? 26) - 26) * 2.1;
  const humidityPenalty = Math.abs((sensors.humidity ?? 65) - 65) * 0.65;
  const moisturePenalty = Math.abs((sensors.soilMoisture ?? 48) - 48) * 0.8;
  return Math.max(72, Math.round(100 - temperaturePenalty - humidityPenalty - moisturePenalty));
}
