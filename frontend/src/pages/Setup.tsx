import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/api/client';
import { Lock, User, ShieldCheck } from 'lucide-react';

interface SetupProps {
  onConfigured: () => void;
}

export function Setup({ onConfigured }: SetupProps) {
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
      setError('No se pudo guardar. Verificá que el servidor esté corriendo.');
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
          <h1 className="text-2xl font-bold">iRacing Dashboard</h1>
          <p className="text-sm text-muted-foreground">Conectate con tu cuenta de iRacing</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Configurar cuenta</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Email de iRacing</label>
                <div className="relative">
                  <User size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="email"
                    placeholder="tu@email.com"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="pl-9"
                    autoComplete="username"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Contraseña</label>
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
                {loading ? 'Guardando…' : 'Conectar'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Security notice */}
        <div className="flex items-start gap-2 rounded-lg bg-muted/50 p-3 text-xs text-muted-foreground">
          <ShieldCheck size={14} className="mt-0.5 shrink-0 text-emerald-400" />
          <p>
            Tus credenciales se guardan <strong className="text-foreground">cifradas</strong> en tu
            computadora. Nunca se envían a ningún servidor externo ni se suben a GitHub.
          </p>
        </div>

        <p className="text-center text-xs text-muted-foreground">
          Requiere que 2FA esté desactivado en{' '}
          <span className="text-primary">iracing.com → Account → Security</span>
        </p>
      </div>
    </div>
  );
}
