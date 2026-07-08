-- Cross-venture identity profiles — portfolio_spine (ldfruywifqnfpwsfgmdl)
-- SSOT: data/cross-domain-auth-surfaces-v1.json
-- Law: separate from campaign_automations profiles (video-ad factory)

CREATE TABLE IF NOT EXISTS identity_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  venture TEXT NOT NULL CHECK (venture IN ('sourcea', 'noetfield', 'trustfield')),
  role TEXT NOT NULL DEFAULT 'member',
  display_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_identity_profiles_venture ON identity_profiles(venture);

ALTER TABLE identity_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "identity_profiles_select_own"
  ON identity_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "identity_profiles_update_own"
  ON identity_profiles FOR UPDATE
  USING (auth.uid() = id);

-- Service role / auth hook inserts on signup (browser uses anon + RLS read own only)
CREATE POLICY "identity_profiles_insert_self"
  ON identity_profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

CREATE OR REPLACE FUNCTION public.handle_new_identity_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_venture TEXT;
  v_name TEXT;
BEGIN
  v_venture := COALESCE(
    NEW.raw_user_meta_data->>'venture',
    NEW.raw_app_meta_data->>'venture',
    'sourcea'
  );
  IF v_venture NOT IN ('sourcea', 'noetfield', 'trustfield') THEN
    v_venture := 'sourcea';
  END IF;
  v_name := COALESCE(
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'name',
    split_part(NEW.email, '@', 1)
  );
  INSERT INTO public.identity_profiles (id, venture, role, display_name)
  VALUES (NEW.id, v_venture, 'member', v_name)
  ON CONFLICT (id) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    updated_at = now();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created_identity ON auth.users;
CREATE TRIGGER on_auth_user_created_identity
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_identity_user();
