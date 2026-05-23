import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { activityLogs, alerts, gpioPins, historySeries, sensorSnapshot } from '../assets/greenhouseData';
import { greenhouseApi } from '../services/api';
import { deriveAutomationState } from '../utils/automation';

const GreenhouseContext = createContext(null);

export function GreenhouseProvider({ children }) {
  const [sensors, setSensors] = useState(sensorSnapshot);
  const [history, setHistory] = useState(historySeries);
  const [status, setStatus] = useState({});
  const [autoMode, setAutoMode] = useState(true);
  const [devices, setDevices] = useState({
    drip: false,
    rain: false,
    cooler: true,
    led: true,
  });
  const [thresholds, setThresholds] = useState({
    temperature: 30,
    moisture: 40,
    light: 420,
  });

  const refresh = useCallback(async () => {
    const [sensorData, historyData, statusData] = await Promise.all([
      greenhouseApi.getSensors(),
      greenhouseApi.getHistory(),
      greenhouseApi.getStatus(),
    ]);
    setSensors((current) => ({ ...current, ...sensorData }));
    setHistory(Array.isArray(historyData) ? historyData : historySeries);
    setStatus(statusData);
    if (statusData?.devices) {
      setDevices((current) => ({ ...current, ...statusData.devices }));
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!autoMode) return;
    const nextAutomation = deriveAutomationState(sensors, thresholds);
    const changed = Object.entries(nextAutomation).filter(([device, enabled]) => devices[device] !== enabled);

    if (changed.length === 0) return;

    setDevices((current) => ({ ...current, ...nextAutomation }));

    changed.forEach(([device, enabled]) => {
      greenhouseApi.setDevice(device, enabled, 'auto').then((response) => {
        if (response.data?.devices) {
          setDevices((current) => ({ ...current, ...response.data.devices }));
        }
      }).catch((error) => {
        console.info(`${device} avtomatika buyrug'i backendga yetmadi:`, error.message);
      });
    });
  }, [autoMode, devices, sensors, thresholds]);

  const setDevice = async (device, enabled) => {
    setDevices((current) => ({ ...current, [device]: enabled }));
    try {
      const response = await greenhouseApi.setDevice(device, enabled, 'site');
      if (response.data?.devices) {
        setDevices((current) => ({ ...current, ...response.data.devices }));
      }
    } catch (error) {
      console.info(`${device} qurilmasi lokal navbatga qo'yildi:`, error.message);
    }
  };

  const value = useMemo(
    () => ({
      sensors,
      history,
      status,
      alerts,
      activityLogs,
      gpioPins: status.gpio || gpioPins,
      devices,
      autoMode,
      thresholds,
      refresh,
      setDevice,
      setAutoMode,
      setThresholds,
    }),
    [autoMode, devices, history, refresh, sensors, status, thresholds],
  );

  return <GreenhouseContext.Provider value={value}>{children}</GreenhouseContext.Provider>;
}

export function useGreenhouse() {
  const value = useContext(GreenhouseContext);
  if (!value) {
    throw new Error('useGreenhouse GreenhouseProvider ichida ishlatilishi kerak');
  }
  return value;
}
