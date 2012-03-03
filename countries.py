from logsparser.lognormalizer import LogNormalizer as LN
import GeoIP

normalizer = LN('/home/kura//.virtualenvs/ssh-attack-visualisation/share/logsparser/normalizers/')
auth_logs = open('/home/kura/workspace/ssh-attack-visualisation/logs/auth.log.combined', 'r')
locator = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)

for log in auth_logs:
    l = {'raw' : log[:-1] } # remove the ending \n
    normalizer.normalize(l)
    print locator.country_name_by_addr(l['source_ip'])
