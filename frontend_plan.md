# IoT Data Ingestion & Streaming Service - Frontend Development Plan

This document outlines the complete frontend implementation plan for building a
**React-based Web Application** that interfaces with the IoT Data Ingestion & 
Real-Time Streaming Service backend.

The frontend will provide:
- User authentication and management
- IoT data visualization dashboard
- Real-time data streaming via WebSockets
- Device/user management interface

------------------------------------------------------------------------

# Tech Stack

  Technology         Purpose
  ------------------ --------------------------
  React 18+          Frontend framework
  Vite               Build tool and dev server
  TypeScript         Type safety
  Tailwind CSS       Styling
  React Router       Client-side routing
  Recharts           Data visualization charts
  Socket.io-client   WebSocket client
  Axios              HTTP client
  React Query        Server state management
  Zustand            Client state management
  React Hook Form    Form handling
  Zod                Schema validation

------------------------------------------------------------------------

# Phase 1: Project Setup

## 1. Initialize Project

Create React + TypeScript project with Vite:

    npm create vite@latest frontend -- --template react-ts
    cd frontend
    npm install

## 2. Install Dependencies

    npm install react-router-dom axios socket.io-client recharts
    npm install @tanstack/react-query zustand react-hook-form zod
    npm install @hookform/resolvers clsx tailwind-merge
    npm install -D tailwindcss postcss autoprefixer

## 3. Configure Tailwind CSS

Initialize and configure Tailwind:

    npx tailwindcss init -p

Update tailwind.config.js:

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Add to index.css:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

------------------------------------------------------------------------

# Phase 2: Project Structure

## Directory Structure

    frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ui/            # Reusable UI components
    │   │   ├── auth/          # Authentication components
    │   │   ├── dashboard/     # Dashboard components
    │   │   ├── iot/           # IoT data components
    │   │   └── layout/        # Layout components
    │   ├── pages/             # Page components
    │   ├── hooks/            # Custom hooks
    │   ├── services/          # API and WebSocket services
    │   ├── stores/            # Zustand stores
    │   ├── types/             # TypeScript types
    │   ├── utils/             # Utility functions
    │   ├── App.tsx
    │   └── main.tsx
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── tailwind.config.js

------------------------------------------------------------------------

# Phase 3: Authentication

## 1. Auth Service

Create API service for login:

```typescript
// src/services/api.ts
import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
};
```

## 2. Auth Store

Create Zustand store for auth state:

```typescript
// src/stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      setToken: (token) => set({ token }),
      logout: () => set({ token: null }),
    }),
    { name: 'auth-storage' }
  )
);
```

## 3. Login Page

Create login page component:

    src/pages/Login.tsx

Features:
- Username/password form
- Form validation with Zod
- Error handling
- Loading state
- Redirect on success

## 4. Protected Routes

Create route guard component:

    src/components/auth/ProtectedRoute.tsx

------------------------------------------------------------------------

# Phase 4: Layout & Navigation

## 1. App Layout

Create main layout with sidebar navigation:

    src/components/layout/AppLayout.tsx

Components:
- Sidebar with navigation links
- Header with user info and logout
- Main content area

## 2. Navigation Items

- Dashboard - Overview and statistics
- Users - User management
- IoT Data - Data visualization
- Settings - App configuration

------------------------------------------------------------------------

# Phase 5: Dashboard

## 1. Dashboard Page

Create main dashboard:

    src/pages/Dashboard.tsx

Components:
- Summary cards (total users, active devices, data points)
- Recent activity feed
- Quick stats charts

## 2. Statistics Cards

Create reusable stat card component:

    src/components/ui/StatCard.tsx

------------------------------------------------------------------------

# Phase 6: User Management

## 1. User List Page

Create user management page:

    src/pages/Users.tsx

Features:
- List all users with pagination
- Search/filter users
- Create new user modal
- Edit user modal
- Delete user confirmation

## 2. User API Service

```typescript
// src/services/userApi.ts
export const userApi = {
  getUsers: () => api.get('/users'),
  getUser: (userId: string) => api.get(`/users/${userId}`),
  createUser: (data: CreateUserDto) => api.post('/users', data),
  updateUser: (userId: string, data: UpdateUserDto) => 
    api.put(`/users/${userId}`, data),
};
```

## 3. User Components

Create:
- UserTable.tsx - Display users in table
- UserForm.tsx - Create/edit user form
- UserCard.tsx - User summary card

------------------------------------------------------------------------

# Phase 7: IoT Data Visualization

## 1. WebSocket Service

Create WebSocket service for real-time data:

```typescript
// src/services/websocket.ts
import { io, Socket } from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;

  connect(token: string) {
    this.socket = io(import.meta.env.VITE_WS_URL || 'ws://localhost:8000', {
      auth: { token },
      transports: ['websocket'],
    });
  }

  subscribe(userId: string, callback: (data: any) => void) {
    this.socket?.emit('subscribe', userId);
    this.socket?.on('new_data', callback);
  }

  disconnect() {
    this.socket?.disconnect();
  }
}

export const wsService = new WebSocketService();
```

## 2. IoT Data Page

Create IoT data visualization page:

    src/pages/IoTData.tsx

Features:
- Real-time data display
- Historical data chart
- Metric filters
- Date range selector
- Data table with pagination

## 3. Chart Components

Create visualization components:

    src/components/iot/LineChart.tsx
    src/components/iot/MetricCard.tsx
    src/components/iot/DataTable.tsx

## 4. Real-time Updates

Create hook for real-time data:

```typescript
// src/hooks/useRealtimeData.ts
import { useEffect, useState } from 'react';
import { wsService } from '../services/websocket';

export const useRealtimeData = (userId: string) => {
  const [data, setData] = useState<IoTData[]>([]);

  useEffect(() => {
    wsService.subscribe(userId, (newData) => {
      setData((prev) => [newData, ...prev].slice(0, 100));
    });

    return () => wsService.unsubscribe(userId);
  }, [userId]);

  return data;
};
```

------------------------------------------------------------------------

# Phase 8: API Integration

## 1. React Query Setup

Configure React Query provider:

```typescript
// src/App.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}
```

## 2. API Hooks

Create custom hooks for API calls:

    src/hooks/useUsers.ts
    src/hooks/useIoTData.ts
    src/hooks/useAuth.ts

------------------------------------------------------------------------

# Phase 9: UI Components

## 1. Reusable Components

Create base UI components:

    src/components/ui/Button.tsx
    src/components/ui/Input.tsx
    src/components/ui/Modal.tsx
    src/components/ui/Table.tsx
    src/components/ui/Card.tsx
    src/components/ui/Spinner.tsx

## 2. Form Components

Create form-specific components:

    src/components/ui/FormField.tsx
    src/components/ui/Select.tsx

------------------------------------------------------------------------

# Phase 10: State Management

## 1. Store Structure

Create Zustand stores:

    src/stores/authStore.ts      - Authentication state
    src/stores/userStore.ts      - User management state
    src/stores/iotStore.ts       - IoT data state
    src/stores/uiStore.ts       - UI state (modals, sidebar)

## 2. Store Examples

```typescript
// src/stores/iotStore.ts
import { create } from 'zustand';

interface IoTStore {
  selectedUserId: string | null;
  dateRange: { start: Date; end: Date };
  metrics: string[];
  setSelectedUser: (userId: string) => void;
  setDateRange: (start: Date, end: Date) => void;
  setMetrics: (metrics: string[]) => void;
}

export const useIoTStore = create<IoTStore>((set) => ({
  selectedUserId: null,
  dateRange: { start: new Date(), end: new Date() },
  metrics: ['metric_1', 'metric_2', 'metric_3'],
  setSelectedUser: (userId) => set({ selectedUserId: userId }),
  setDateRange: (start, end) => set({ dateRange: { start, end } }),
  setMetrics: (metrics) => set({ metrics }),
}));
```

------------------------------------------------------------------------

# Phase 11: Testing

## 1. Test Setup

Install testing libraries:

    npm install -D @testing-library/react @testing-library/jest-dom
    npm install -D vitest jsdom

## 2. Test Coverage

Test files:

    src/__tests__/components/Button.test.tsx
    src/__tests__/pages/Login.test.tsx
    src/__tests__/hooks/useAuth.test.ts
    src/__tests__/services/api.test.ts

## 3. Test Types

- Unit tests for components
- Integration tests for API calls
- E2E tests for critical flows

------------------------------------------------------------------------

# Phase 12: Build & Deployment

## 1. Environment Variables

Create .env file:

    VITE_API_URL=http://localhost:8000
    VITE_WS_URL=ws://localhost:8000

## 2. Build for Production

    npm run build

## 3. Docker Setup (Optional)

Create Dockerfile:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

------------------------------------------------------------------------

# Suggested Directory Structure (Final)

    frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ui/
    │   │   │   ├── Button.tsx
    │   │   │   ├── Input.tsx
    │   │   │   ├── Modal.tsx
    │   │   │   ├── Table.tsx
    │   │   │   └── Card.tsx
    │   │   ├── auth/
    │   │   │   ├── LoginForm.tsx
    │   │   │   └── ProtectedRoute.tsx
    │   │   ├── dashboard/
    │   │   │   ├── StatCard.tsx
    │   │   │   └── ActivityFeed.tsx
    │   │   ├── iot/
    │   │   │   ├── LineChart.tsx
    │   │   │   ├── MetricCard.tsx
    │   │   │   └── DataTable.tsx
    │   │   └── layout/
    │   │       ├── AppLayout.tsx
    │   │       ├── Sidebar.tsx
    │   │       └── Header.tsx
    │   ├── pages/
    │   │   ├── Dashboard.tsx
    │   │   ├── Login.tsx
    │   │   ├── Users.tsx
    │   │   ├── IoTData.tsx
    │   │   └── Settings.tsx
    │   ├── hooks/
    │   │   ├── useAuth.ts
    │   │   ├── useUsers.ts
    │   │   ├── useIoTData.ts
    │   │   └── useRealtimeData.ts
    │   ├── services/
    │   │   ├── api.ts
    │   │   ├── userApi.ts
    │   │   ├── iotApi.ts
    │   │   └── websocket.ts
    │   ├── stores/
    │   │   ├── authStore.ts
    │   │   ├── userStore.ts
    │   │   ├── iotStore.ts
    │   │   └── uiStore.ts
    │   ├── types/
    │   │   ├── user.ts
    │   │   └── iotData.ts
    │   ├── utils/
    │   │   ├── formatters.ts
    │   │   └── validators.ts
    │   ├── App.tsx
    │   └── main.tsx
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── .env.example

------------------------------------------------------------------------

# Implementation Priority

1. **Week 1**: Project setup, routing, auth
2. **Week 2**: Dashboard, layout components
3. **Week 3**: User management pages
4. **Week 4**: IoT data visualization
5. **Week 5**: Real-time WebSocket integration
6. **Week 6**: Testing, refinements, deployment

------------------------------------------------------------------------

# Future Enhancements

- Dark mode support
- Mobile responsive design
- Data export functionality
- Advanced filtering and search
- Multiple chart types
- Notification system
- Performance optimization