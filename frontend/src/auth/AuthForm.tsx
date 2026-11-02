import { FormEvent, useState } from 'react';
import { ArrowRight, Eye, EyeOff, Loader2, Lock, Mail } from 'lucide-react';
import { supabase } from './supabase';

type AuthMode = 'login' | 'signup';

interface AuthFormProps {
  mode: AuthMode;
  onSwitch: () => void;
}

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const minimumPasswordLength = 8;

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    if (error.message.toLowerCase().includes('invalid login credentials')) {
      return 'That email or password is not correct.';
    }
    if (error.message.toLowerCase().includes('user already registered')) {
      return 'An account with this email already exists. Try signing in instead.';
    }
    return error.message;
  }
  return 'Something went wrong. Please try again.';
}

export default function AuthForm({ mode, onSwitch }: AuthFormProps) {
  const isSignup = mode === 'signup';
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setMessage('');

    if (!emailPattern.test(email.trim())) {
      setError('Enter a valid email address.');
      return;
    }
    if (password.length < minimumPasswordLength) {
      setError(`Password must be at least ${minimumPasswordLength} characters.`);
      return;
    }
    if (isSignup && password !== confirmation) {
      setError('Passwords do not match.');
      return;
    }

    setIsSubmitting(true);
    try {
      if (isSignup) {
        const { data, error: signUpError } = await supabase.auth.signUp({
          email: email.trim(),
          password,
        });
        if (signUpError) throw signUpError;
        if (!data.session) {
          setMessage('Account created. Check your email to confirm your address, then sign in.');
        }
      } else {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });
        if (signInError) throw signInError;
      }
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-shell">
      <div className="auth-atmosphere auth-atmosphere-one" />
      <div className="auth-atmosphere auth-atmosphere-two" />
      <section className="auth-card" aria-labelledby="auth-title">
        <div className="auth-brand">
          <img className="auth-brand-icon" src="/krishna-code-logo.svg" alt="" />
          <span>Krishna Code AI</span>
        </div>
        <div className="auth-kicker"><span /> Secure engineering workspace</div>
        <h1 id="auth-title">{isSignup ? 'Build what matters.' : 'Welcome back.'}</h1>
        <p className="auth-intro">
          {isSignup
            ? 'Create your account and start turning product ideas into working software.'
            : 'Sign in to continue building with your agent network.'}
        </p>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <label className="auth-field">
            <span>Email address</span>
            <span className="auth-input-wrap">
              <Mail size={17} aria-hidden="true" />
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@company.com"
                autoComplete="email"
                required
              />
            </span>
          </label>

          <label className="auth-field">
            <span>Password</span>
            <span className="auth-input-wrap">
              <Lock size={17} aria-hidden="true" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="At least 8 characters"
                autoComplete={isSignup ? 'new-password' : 'current-password'}
                required
              />
              <button
                type="button"
                className="auth-visibility"
                onClick={() => setShowPassword((visible) => !visible)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
              </button>
            </span>
          </label>

          {isSignup && (
            <label className="auth-field">
              <span>Confirm password</span>
              <span className="auth-input-wrap">
                <Lock size={17} aria-hidden="true" />
                <input
                  type={showConfirmation ? 'text' : 'password'}
                  value={confirmation}
                  onChange={(event) => setConfirmation(event.target.value)}
                  placeholder="Repeat your password"
                  autoComplete="new-password"
                  required
                />
                <button
                  type="button"
                  className="auth-visibility"
                  onClick={() => setShowConfirmation((visible) => !visible)}
                  aria-label={showConfirmation ? 'Hide password confirmation' : 'Show password confirmation'}
                >
                  {showConfirmation ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </span>
            </label>
          )}

          {error && <p className="auth-message auth-message-error" role="alert">{error}</p>}
          {message && <p className="auth-message auth-message-success" role="status">{message}</p>}

          <button className="auth-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? <Loader2 className="auth-spinner" size={18} /> : <span>{isSignup ? 'Create account' : 'Sign in'}</span>}
            {!isSubmitting && <ArrowRight size={18} />}
          </button>
        </form>

        <p className="auth-switch">
          {isSignup ? 'Already have an account?' : 'New to Krishna Code AI?'}
          <button type="button" onClick={onSwitch}>{isSignup ? 'Sign in' : 'Create an account'}</button>
        </p>
        <p className="auth-footnote">Your session is encrypted and secured by Supabase.</p>
      </section>
    </main>
  );
}
