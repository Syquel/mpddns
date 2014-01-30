import syslog
import json
import traceback

class CatalogEntry:
    def __init__(self, password):
        self.password = password
        self.ip = None
        self.static = (not self.password)

    def updateIp(self, ip):
        if not self.static:
            self.ip = ip

    def getIp(self):
        return self.ip

    def getPassword(self):
        return self.password

class Catalog:
    def __init__(self, data, cacheFile):
        self.catalog = {}
        self.cacheFile = cacheFile
        
        cacheData = {}
        try:
            with open(self.cacheFile, 'r') as f:
                cacheData = json.load(f)
        except:
            pass

        for domain, config in data.iteritems():
            domain = domain.lower()

            if not config.get("password"):
                syslog.syslog(syslog.LOG_INFO, "'%s' has no password given. Using static DNS." % domain)

            self.catalog[domain] = CatalogEntry(config.get("password"))

            if config.get("ip"):
                self.catalog[domain].updateIp(config["ip"]);
            elif domain in cacheData:
                self.catalog[domain].updateIp(cacheData[domain])

    def updateIp(self, domain, ip):
        domain = domain.lower()
        entry = self.catalog.get(domain)
        if entry is None:
            return False

        if entry.getIp() == ip:
            return True
        
        entry.updateIp(ip)
        syslog.syslog("Updated '%s' with '%s'" % (domain, ip))

        try:
            with open(self.cacheFile, 'w') as f:
                json.dump({domain: entry.getIp() for domain, entry in self.catalog.iteritems()}, f)
        except:
            syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

        return True

    def getIp(self, domain):
        domain = domain.lower()
        entry = self.catalog.get(domain)
        if entry:
            return entry.getIp()
        return None

    def getPassword(self, domain):
        domain = domain.lower()
        entry = self.catalog.get(domain)
        if entry:
            return entry.getPassword()
        return None
