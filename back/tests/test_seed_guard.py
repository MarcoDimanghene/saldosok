import unittest

from back.seed import _validate_demo_seed_target


class DemoSeedGuardTests(unittest.TestCase):
    def test_seed_requires_explicit_development_opt_in(self):
        with self.assertRaises(RuntimeError):
            _validate_demo_seed_target(
                "sqlite:///local.db",
                app_env="development",
                allow_demo_seed=False,
            )

        _validate_demo_seed_target(
            "sqlite:///local.db",
            app_env="development",
            allow_demo_seed=True,
        )

    def test_seed_rejects_production_and_remote_databases(self):
        for app_env, database_url in (
            ("production", "sqlite:///local.db"),
            ("development", "postgresql://user:password@db.example.com/app"),
        ):
            with self.subTest(app_env=app_env, database_url=database_url):
                with self.assertRaises(RuntimeError):
                    _validate_demo_seed_target(
                        database_url,
                        app_env=app_env,
                        allow_demo_seed=True,
                    )


if __name__ == "__main__":
    unittest.main()
