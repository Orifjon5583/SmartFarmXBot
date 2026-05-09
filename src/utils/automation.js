export function deriveAutomationState(sensors, thresholds = {}) {
  const temperatureLimit = thresholds.temperature ?? 30;
  const moistureLimit = thresholds.moisture ?? 40;
  const lightLimit = thresholds.light ?? 420;

  return {
    fan: Number(sensors.temperature) > temperatureLimit,
    pump: Number(sensors.soilMoisture) < moistureLimit,
    light: Number(sensors.light) < lightLimit,
  };
}

export function healthScore(sensors) {
  const temperaturePenalty = Math.abs((sensors.temperature ?? 26) - 26) * 2.1;
  const humidityPenalty = Math.abs((sensors.humidity ?? 65) - 65) * 0.65;
  const moisturePenalty = Math.abs((sensors.soilMoisture ?? 48) - 48) * 0.8;
  return Math.max(72, Math.round(100 - temperaturePenalty - humidityPenalty - moisturePenalty));
}
