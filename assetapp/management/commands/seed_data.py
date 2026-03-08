"""
python manage.py seed_data

Creates sample counties, sub-counties, CHUs and one user per role.
All passwords: chis1234
"""
from django.core.management.base import BaseCommand
from assetapp.models import County, SubCounty, CommunityHealthUnit, User, Role


class Command(BaseCommand):
    help = 'Seed sample data for testing'

    def handle(self, *args, **kwargs):
        # ── Locations ──────────────────────────────────────────────────
        kisumu, _ = County.objects.get_or_create(name='Kisumu')
        nakuru, _ = County.objects.get_or_create(name='Nakuru')

        kisumu_west, _ = SubCounty.objects.get_or_create(name='Kisumu West', county=kisumu)
        kisumu_east, _ = SubCounty.objects.get_or_create(name='Kisumu East', county=kisumu)
        nakuru_east, _ = SubCounty.objects.get_or_create(name='Nakuru East', county=nakuru)

        chu1, _ = CommunityHealthUnit.objects.get_or_create(name='Obunga CHU',        subcounty=kisumu_west)
        chu2, _ = CommunityHealthUnit.objects.get_or_create(name='Manyatta CHU',      subcounty=kisumu_west)
        chu3, _ = CommunityHealthUnit.objects.get_or_create(name='Kolwa East CHU',    subcounty=kisumu_east)
        chu4, _ = CommunityHealthUnit.objects.get_or_create(name='Nakuru Town CHU',   subcounty=nakuru_east)

        # ── Users ──────────────────────────────────────────────────────
        admin = self._user('admin', 'System', 'Admin', Role.COUNTRY_ADMIN)

        cf = self._user('county_kisumu', 'County Focal', 'Kisumu', Role.COUNTY_FOCAL)
        cf.county = kisumu; cf.save()

        scf = self._user('scf_kisumu_west', 'SubCounty Focal', 'Kisumu West', Role.SUBCOUNTY_FOCAL)
        scf.subcounty = kisumu_west; scf.county = kisumu; scf.save()

        cha = self._user('cha_obunga', 'Jane', 'Wanjiru', Role.CHA)
        cha.subcounty = kisumu_west; cha.county = kisumu
        cha.save()
        cha.chus.set([chu1, chu2])

        self.stdout.write(self.style.SUCCESS(
            '\n✅ Seed data created! Password for all users: chis1234\n\n'
            '  admin             → Country Admin\n'
            '  county_kisumu     → County Focal (Kisumu)\n'
            '  scf_kisumu_west   → Sub-County Focal (Kisumu West)\n'
            '  cha_obunga        → CHA (Obunga + Manyatta CHU)\n'
        ))

    def _user(self, username, first, last, role):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'first_name': first, 'last_name': last, 'role': role}
        )
        if created:
            user.set_password('chis1234')
            user.save()
        return user