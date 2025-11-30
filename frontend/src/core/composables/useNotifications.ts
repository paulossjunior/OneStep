import { ref } from 'vue';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

const notifications = ref<Notification[]>([]);

export function useNotifications() {
  const add = (notification: Omit<Notification, 'id'>) => {
    const id = `notification-${Date.now()}-${Math.random()}`;
    const newNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration || 5000,
    };

    notifications.value.push(newNotification);

    // Auto remove after duration
    if (newNotification.duration > 0) {
      setTimeout(() => {
        remove(id);
      }, newNotification.duration);
    }

    return id;
  };

  const remove = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index > -1) {
      notifications.value.splice(index, 1);
    }
  };

  const clear = () => {
    notifications.value = [];
  };

  const success = (message: string, duration?: number) => {
    return add({ type: 'success', message, duration });
  };

  const error = (message: string, duration?: number) => {
    return add({ type: 'error', message, duration });
  };

  const warning = (message: string, duration?: number) => {
    return add({ type: 'warning', message, duration });
  };

  const info = (message: string, duration?: number) => {
    return add({ type: 'info', message, duration });
  };

  return {
    notifications,
    add,
    remove,
    clear,
    success,
    error,
    warning,
    info,
  };
}
