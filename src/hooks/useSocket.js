import { useEffect, useMemo, useState } from 'react';
import { createGreenhouseSocket } from '../services/api';

export function useSocket(channel, handler) {
  const socket = useMemo(() => createGreenhouseSocket(), []);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    socket.connect();
    socket.on('connect', () => setConnected(true));
    socket.on('disconnect', () => setConnected(false));

    if (channel && handler) {
      socket.on(channel, handler);
    }

    return () => {
      if (channel && handler) {
        socket.off(channel, handler);
      }
      socket.disconnect();
    };
  }, [channel, handler, socket]);

  return { socket, connected };
}
