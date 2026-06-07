import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/api/client';
import { Lock, User, ShieldCheck } from 'lucide-react';

interface SetupProps {
  onConfigured: () => void;
}

export function Setup({ onConfigured }: SetupProps) {
  const { t } = useTranslation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;
    setLoading(true);
    setError('');
    try {
      await api.auth.save(username, password);
      onConfigured();
    } catch {
      setError(t('setup.error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo */}
        <div className="text-center space-y-2">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary">
            <span className="text-2xl font-bold text-primary-foreground">iR</span>
          </div>
          <h1 className="text-2xl font-bold">{t('setup.appTitle')}</h1>
          <p className="text-sm text-muted-foreground">{t('setup.subtitle')}</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">{t('setup.cardTitle')}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">{t('setup.emailLabel')}</label>
                <div className="relative">
                  <User size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="email"
                    placeholder={t('setup.emailPlaceholder')}
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="pl-9"
                    autoComplete="username"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('setup.passwordLabel')}</label>
                <div className="relative">
                  <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-9"
                    autoComplete="current-password"
                  />
                </div>
              </div>

              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}

              <Button type="submit" className="w-full" disabled={loading || !username || !password}>
                {loading ? t('setup.connecting') : t('setup.connect')}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Security notice */}
        <div className="flex items-start gap-2 rounded-lg bg-muted/50 p-3 text-xs text-muted-foreground">
          <ShieldCheck size={14} className="mt-0.5 shrink-0 text-emerald-400" />
          <p>
            {t('setup.securityNoticePrefix')}<strong className="text-foreground">{t('setup.securityNoticeBold')}</strong>{t('setup.securityNoticeSuffix')}
          </p>
        </div>

        <p className="text-center text-xs text-muted-foreground">
          {t('setup.twoFaNotice')}{' '}
          <span className="text-primary">iracing.com → Account → Security</span>
        </p>
      </div>
    </div>
  );
}
