export function deriveAutomationState(sensors, thresholds = {}) {
  const temperatureLimit = thresholds.temperature ?? 30;
  const moistureLimit = thresholds.moisture ?? 40;
  const lightLimit = thresholds.light ?? 420;

  return {
    cooler: Number(sensors.temperature) > temperatureLimit,
    drip: Number(sensors.soilMoisture) < moistureLimit,
    rain: Number(sensors.soilMoisture) < moistureLimit - 12,
    led: Number(sensors.light) < lightLimit,
  };
}

export function healthScore(sensors) {
  const temperaturePenalty = Math.abs((sensors.temperature ?? 26) - 26) * 2.1;
  const humidityPenalty = Math.abs((sensors.humidity ?? 65) - 65) * 0.65;
  const moisturePenalty = Math.abs((sensors.soilMoisture ?? 48) - 48) * 0.8;
  return Math.max(72, Math.round(100 - temperaturePenalty - humidityPenalty - moisturePenalty));
}
