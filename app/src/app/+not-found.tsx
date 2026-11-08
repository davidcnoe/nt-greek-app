import { Redirect } from 'expo-router';

// Any unknown address (for example a host's own page path) opens the home screen.
export default function NotFound() {
  return <Redirect href="/" />;
}
