"""
Smart Query Router

Routes queries to appropriate specialist models or general knowledge systems.
Detects domain (NixOS, Programming, DevOps, etc.) and routes intelligently.
"""

from enum import Enum
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import re
import os


class Domain(Enum):
    """Available specialist domains"""
    NIXOS = "nixos"
    PROGRAMMING = "programming"
    DEVOPS = "devops"
    NETWORKING = "networking"
    DATABASE = "database"
    SECURITY = "security"
    GENERAL = "general"
    UNCLEAR = "unclear"


@dataclass
class RouteResult:
    """Result of query routing"""
    domain: Domain
    confidence: float  # 0.0 - 1.0
    specialist_model: Optional[str] = None  # Which model to use
    context_hint: Optional[str] = None  # Hint for response formatting
    should_offer_nixos_context: bool = False  # Should we offer NixOS-specific solution?


class QueryRouter:
    """
    Routes queries to appropriate specialist domains.

    Strategy:
    1. Detect explicit domain keywords (high confidence)
    2. Detect implicit domain patterns (medium confidence)
    3. When unclear, route to general with low confidence
    4. Always check if NixOS context would be helpful
    """

    def __init__(self):
        """Initialize router with domain keywords"""

        # NixOS-specific keywords (highest priority)
        self.nixos_keywords = {
            # Core NixOS terms
            'nixos', 'nix-env', 'nix-shell', 'nixpkgs',
            'derivation', 'nixos-rebuild', 'configuration.nix',
            'flake.nix', 'flake', 'home-manager',

            # NixOS operations
            'nixos-generate-config', 'nixos-install',
            'nix-channel', 'nix-collect-garbage',

            # Nix language
            'stdenv', 'mkderivation', 'buildinputs',
            'fetchurl', 'fetchgit', 'overlay',

            # NixOS services
            'systemd.services', 'networking.firewall',
            'services.nginx', 'services.postgresql'
        }

        # Programming keywords (expanded)
        self.programming_keywords = {
            # Languages
            'python', 'javascript', 'typescript', 'rust', 'go', 'golang',
            'java', 'c++', 'cpp', 'c#', 'csharp', 'ruby', 'php', 'swift',
            'kotlin', 'scala', 'haskell', 'elixir', 'perl', 'lua',

            # Concepts
            'debug', 'debugging', 'compile', 'compilation', 'build',
            'syntax error', 'runtime error', 'exception', 'traceback',
            'function', 'class', 'method', 'variable', 'constant',
            'algorithm', 'data structure', 'recursion', 'iteration',
            'async', 'await', 'promise', 'callback', 'iterator',
            'closure', 'decorator', 'generator', 'coroutine',

            # Patterns & Paradigms
            'oop', 'object-oriented', 'functional programming',
            'design pattern', 'mvc', 'mvvm', 'dependency injection',
            'singleton', 'factory', 'observer', 'strategy',

            # Tools & Concepts
            'lint', 'linter', 'formatter', 'type checking',
            'unit test', 'integration test', 'mock', 'stub',
            'refactor', 'optimize', 'performance', 'benchmark',
            'memory leak', 'garbage collection', 'profiling'
        }

        # DevOps keywords (expanded)
        self.devops_keywords = {
            # Containers & Orchestration
            'docker', 'dockerfile', 'docker-compose', 'podman',
            'kubernetes', 'k8s', 'kubectl', 'helm', 'kustomize',
            'container', 'containerization', 'image', 'registry',
            'pod', 'deployment', 'statefulset', 'daemonset',

            # CI/CD
            'ci/cd', 'ci', 'cd', 'pipeline', 'build pipeline',
            'jenkins', 'gitlab', 'gitlab-ci', 'github actions',
            'circleci', 'travis', 'buildkite', 'drone',
            'argocd', 'flux', 'tekton', 'spinnaker',

            # Infrastructure as Code
            'terraform', 'iac', 'infrastructure as code',
            'ansible', 'puppet', 'chef', 'saltstack',
            'cloudformation', 'pulumi', 'cdk',

            # Monitoring & Observability
            'monitoring', 'observability', 'metrics', 'logs',
            'prometheus', 'grafana', 'alerting', 'alertmanager',
            'datadog', 'new relic', 'splunk', 'elk',
            'loki', 'tempo', 'jaeger', 'tracing',

            # Deployment Strategies
            'deployment', 'rollback', 'rollout',
            'blue-green', 'canary', 'rolling update',
            'a/b testing', 'feature flag',

            # Infrastructure
            'load balancer', 'reverse proxy', 'scaling',
            'autoscaling', 'horizontal scaling', 'vertical scaling',
            'service mesh', 'istio', 'linkerd', 'consul',
            'ingress', 'egress', 'api gateway', 'envoy', 'traefik'
        }

        # Networking keywords (expanded)
        self.networking_keywords = {
            # Hardware & Infrastructure
            'router', 'switch', 'hub', 'bridge', 'modem',
            'firewall', 'iptables', 'nftables', 'pf',
            'access point', 'wifi', 'wireless', 'ethernet',

            # Protocols & Services
            'dns', 'bind', 'unbound', 'dnsmasq', 'resolv',
            'dhcp', 'dhcpd', 'dhcp server', 'dhcp client',
            'tcp', 'udp', 'icmp', 'arp', 'http', 'https',
            'tls', 'ssl', 'quic', 'http2', 'http3',
            'smtp', 'pop3', 'imap', 'ftp', 'sftp', 'scp',

            # VPN & Security
            'vpn', 'wireguard', 'openvpn', 'ipsec', 'l2tp',
            'ssh', 'openssh', 'sshd', 'ssh tunnel',
            'proxy', 'socks', 'http proxy', 'transparent proxy',

            # Network Configuration
            'vlan', 'subnet', 'supernet', 'cidr',
            'gateway', 'default gateway', 'nat', 'pat',
            'port forwarding', 'port mapping', 'upnp',
            'ip address', 'ipv4', 'ipv6', 'static ip', 'dynamic ip',
            'routing', 'routing table', 'route', 'bgp', 'ospf',
            'network interface', 'nic', 'bonding', 'bridging',

            # Troubleshooting & Tools
            'ping', 'traceroute', 'mtr', 'netstat', 'ss',
            'tcpdump', 'wireshark', 'nmap', 'dig', 'nslookup',
            'network latency', 'packet loss', 'bandwidth',
            'mtu', 'mss', 'jumbo frames'
        }

        # Database keywords (expanded)
        self.database_keywords = {
            # SQL Databases
            'sql', 'postgresql', 'postgres', 'mysql', 'mariadb',
            'sqlite', 'mssql', 'sql server', 'oracle',

            # NoSQL Databases
            'mongodb', 'mongo', 'couchdb', 'cassandra',
            'redis', 'memcached', 'dynamodb', 'neo4j',
            'elasticsearch', 'opensearch', 'solr',

            # Query & Operations
            'query', 'select', 'insert', 'update', 'delete',
            'join', 'left join', 'inner join', 'outer join',
            'where', 'group by', 'order by', 'having',
            'subquery', 'cte', 'window function',

            # Schema & Structure
            'schema', 'table', 'column', 'row', 'record',
            'primary key', 'foreign key', 'unique', 'constraint',
            'index', 'composite index', 'full-text index',
            'view', 'materialized view', 'stored procedure', 'trigger',

            # Performance & Optimization
            'optimization', 'query plan', 'explain', 'analyze',
            'slow query', 'n+1 problem', 'caching',
            'connection pool', 'prepared statement',

            # Data Management
            'migration', 'schema migration', 'data migration',
            'backup', 'restore', 'dump', 'import', 'export',
            'replication', 'master-slave', 'master-master',
            'sharding', 'partitioning', 'horizontal scaling',

            # Transactions & Integrity
            'transaction', 'commit', 'rollback', 'savepoint',
            'acid', 'isolation level', 'serializable',
            'deadlock', 'lock', 'mvcc',

            # ORM & Tools
            'orm', 'activerecord', 'sequelize', 'prisma',
            'typeorm', 'sqlalchemy', 'hibernate', 'doctrine'
        }

        # Security keywords (expanded)
        self.security_keywords = {
            # Encryption & Certificates
            'ssl', 'tls', 'certificate', 'cert', 'ca',
            'encryption', 'decrypt', 'aes', 'rsa', 'ecc',
            'pgp', 'gpg', 'gnupg', 'public key', 'private key',
            'https', 'hsts', 'certificate authority',
            'self-signed', 'letsencrypt', 'acme',

            # Authentication & Authorization
            'authentication', 'authorization', 'authn', 'authz',
            'oauth', 'oauth2', 'oidc', 'openid', 'saml',
            'jwt', 'token', 'api key', 'session',
            'password', 'hash', 'salt', 'bcrypt', 'argon2',
            '2fa', 'two-factor', 'mfa', 'multi-factor',
            'sso', 'single sign-on', 'ldap', 'active directory',

            # Firewall & Access Control
            'firewall', 'iptables', 'nftables', 'ufw',
            'selinux', 'apparmor', 'seccomp', 'capability',
            'acl', 'access control', 'permission', 'chmod', 'chown',
            'sudo', 'sudoers', 'privilege escalation',

            # Vulnerabilities & Threats
            'vulnerability', 'cve', 'exploit', 'zero-day',
            'malware', 'virus', 'trojan', 'ransomware',
            'xss', 'csrf', 'sql injection', 'rce',
            'dos', 'ddos', 'mitm', 'man in the middle',
            'phishing', 'social engineering',

            # Security Practices
            'patch', 'update', 'upgrade', 'hardening',
            'penetration test', 'pentest', 'security audit',
            'security scan', 'vulnerability scan',
            'principle of least privilege', 'defense in depth',
            'security by design', 'zero trust'
        }

        # Domain keyword map
        self.domain_keywords = {
            Domain.PROGRAMMING: self.programming_keywords,
            Domain.DEVOPS: self.devops_keywords,
            Domain.NETWORKING: self.networking_keywords,
            Domain.DATABASE: self.database_keywords,
            Domain.SECURITY: self.security_keywords
        }

    def route(self, query: str, conversation_context: Optional[List[Domain]] = None) -> RouteResult:
        """
        Route a query to the appropriate domain with conversation context awareness.

        Args:
            query: User's natural language query
            conversation_context: List of recent conversation domains (most recent last)

        Returns:
            RouteResult with domain, confidence, and routing info
        """
        query_lower = query.lower()

        # 1. Check for explicit NixOS keywords (highest priority)
        nixos_score = self._calculate_keyword_score(query_lower, self.nixos_keywords)
        if nixos_score > 0:
            return RouteResult(
                domain=Domain.NIXOS,
                confidence=min(1.0, nixos_score),
                specialist_model="hrm_nixos_specialist",
                context_hint="nixos_expert",
                should_offer_nixos_context=False  # Already in NixOS context
            )

        # 2. Check other domains
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = self._calculate_keyword_score(query_lower, keywords)
            if score > 0:
                domain_scores[domain] = score

        # 3. Apply conversation context boost for ambiguous queries
        if conversation_context and domain_scores:
            # Debug: show conversation context
            if os.getenv("DEBUG_ROUTING"):
                print(f"[DEBUG] Conversation context: {[d.value for d in conversation_context]}")
                print(f"[DEBUG] Scores before boost: {[(d.value, f'{s:.2f}') for d, s in domain_scores.items()]}")
            domain_scores = self._apply_conversation_boost(domain_scores, conversation_context)
            if os.getenv("DEBUG_ROUTING"):
                print(f"[DEBUG] Scores after boost: {[(d.value, f'{s:.2f}') for d, s in domain_scores.items()]}")

        # 4. If we found a clear domain match
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            confidence = min(1.0, domain_scores[best_domain])

            # Check if this could also be NixOS-related
            should_offer_nixos = self._could_be_nixos_related(query_lower, best_domain)

            return RouteResult(
                domain=best_domain,
                confidence=confidence,
                specialist_model="ollama_general",  # Use general LLM
                context_hint=best_domain.value,
                should_offer_nixos_context=should_offer_nixos
            )

        # 5. No keyword match - use conversation context as primary signal
        if conversation_context:
            # Use most recent non-GENERAL domain from conversation
            recent_domains = [d for d in reversed(conversation_context) if d != Domain.GENERAL]
            if recent_domains:
                # Continue in the same domain
                return RouteResult(
                    domain=recent_domains[0],
                    confidence=0.6,  # Medium confidence from context
                    specialist_model="ollama_general",
                    context_hint=recent_domains[0].value,
                    should_offer_nixos_context=False
                )

        # 6. No clear domain and no context - route to general
        return RouteResult(
            domain=Domain.GENERAL,
            confidence=0.3,  # Low confidence
            specialist_model="ollama_general",
            context_hint="general",
            should_offer_nixos_context=False
        )

    def _apply_conversation_boost(self, domain_scores: Dict[Domain, float],
                                   conversation_context: List[Domain]) -> Dict[Domain, float]:
        """
        Boost domain scores based on recent conversation context.

        If multiple domains have similar scores, prefer the one from recent conversation.
        This helps maintain context in multi-turn conversations.

        Args:
            domain_scores: Current domain scores from keyword matching
            conversation_context: Recent conversation domains (most recent last)

        Returns:
            Adjusted domain scores with conversation boost applied
        """
        if not conversation_context:
            return domain_scores

        # Get recent domains (last 3 turns, excluding GENERAL)
        recent_domains = [d for d in reversed(conversation_context[-3:]) if d != Domain.GENERAL]

        if not recent_domains:
            return domain_scores

        # Calculate boost factors based on recency
        # Most recent: 1.2 boost, second: 0.7 boost, third: 0.4 boost
        # (Very strong boost - conversation context should win in ambiguous cases!)
        boost_factors = [1.2, 0.7, 0.4]

        boosted_scores = domain_scores.copy()

        for i, domain in enumerate(recent_domains[:3]):
            if domain in boosted_scores:
                # Apply boost (decays with recency)
                boost = boost_factors[i]
                boosted_scores[domain] += boost
            else:
                # Domain wasn't detected by keywords, but was in recent conversation
                # Add it with a moderate score based on recency
                boosted_scores[domain] = boost_factors[i]

        return boosted_scores

    def _calculate_keyword_score(self, query: str, keywords: set) -> float:
        """
        Calculate keyword match score with fuzzy matching.

        Returns:
            Score from 0.0 to 2.0+ (can exceed 1.0 for multiple matches)
        """
        score = 0.0

        for keyword in keywords:
            # Exact keyword match
            if keyword in query:
                # Longer keywords count more (more specific)
                score += len(keyword.split()) * 0.3

            # Word boundary match (even better)
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query):
                score += len(keyword.split()) * 0.5

            # Fuzzy match for typos (only for longer keywords)
            if len(keyword) >= 6:  # Only check longer words
                fuzzy_score = self._fuzzy_match(query, keyword)
                if fuzzy_score > 0:
                    score += fuzzy_score * 0.2  # Lower weight for fuzzy matches

        return score

    def _fuzzy_match(self, query: str, keyword: str) -> float:
        """
        Fuzzy match for typo tolerance using edit distance.

        Returns:
            Score from 0.0 to 1.0 based on similarity
        """
        # Split query into words
        words = query.lower().split()

        best_similarity = 0.0

        for word in words:
            # Skip very short words
            if len(word) < 4:
                continue

            # Calculate Levenshtein-like similarity
            similarity = self._calculate_similarity(word, keyword)

            if similarity > best_similarity:
                best_similarity = similarity

        # Only return score if similarity is high enough (>= 80%)
        return best_similarity if best_similarity >= 0.8 else 0.0

    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate similarity between two words (simplified Levenshtein).

        Returns:
            Similarity score from 0.0 to 1.0
        """
        word1 = word1.lower()
        word2 = word2.lower()

        # Quick check: if lengths differ by more than 2, probably not similar
        if abs(len(word1) - len(word2)) > 2:
            return 0.0

        # Count matching characters in roughly the same positions
        matches = 0
        max_len = max(len(word1), len(word2))

        for i in range(min(len(word1), len(word2))):
            if word1[i] == word2[i]:
                matches += 1
            # Allow for common typo: adjacent character swap
            elif i < len(word1) - 1 and i < len(word2) - 1:
                if word1[i] == word2[i+1] and word1[i+1] == word2[i]:
                    matches += 1.5  # Bonus for transposition

        return matches / max_len

    def _could_be_nixos_related(self, query: str, domain: Domain) -> bool:
        """
        Check if a general query could benefit from NixOS-specific context.

        For example:
        - "install docker" → Could offer NixOS docker setup
        - "setup nginx" → Could offer NixOS nginx configuration
        - "configure firewall" → Could offer NixOS firewall setup
        """
        # Installation/setup patterns
        install_patterns = [
            r'\binstall\b', r'\bsetup\b', r'\bconfigure\b',
            r'\bhow to\b', r'\bset up\b', r'\bget\b.*\bworking\b'
        ]

        for pattern in install_patterns:
            if re.search(pattern, query):
                return True

        # If asking about services that NixOS manages well
        nixos_friendly_services = {
            'nginx', 'apache', 'postgresql', 'mysql', 'redis',
            'docker', 'kubernetes', 'gitlab', 'jenkins',
            'vpn', 'wireguard', 'ssh', 'firewall'
        }

        for service in nixos_friendly_services:
            if service in query:
                return True

        return False

    def get_domain_display_name(self, domain: Domain) -> str:
        """Get user-friendly display name for domain"""
        display_names = {
            Domain.NIXOS: "NixOS Expert",
            Domain.PROGRAMMING: "Programming Assistant",
            Domain.DEVOPS: "DevOps Specialist",
            Domain.NETWORKING: "Network Engineer",
            Domain.DATABASE: "Database Consultant",
            Domain.SECURITY: "Security Advisor",
            Domain.GENERAL: "General Assistant",
            Domain.UNCLEAR: "General Assistant"
        }
        return display_names.get(domain, "Assistant")

    def get_domain_emoji(self, domain: Domain) -> str:
        """Get emoji for domain"""
        emojis = {
            Domain.NIXOS: "🔷",
            Domain.PROGRAMMING: "💻",
            Domain.DEVOPS: "🔧",
            Domain.NETWORKING: "🌐",
            Domain.DATABASE: "🗄️",
            Domain.SECURITY: "🔒",
            Domain.GENERAL: "🤖",
            Domain.UNCLEAR: "🤖"
        }
        return emojis.get(domain, "🤖")

    def should_clarify(self, route: RouteResult) -> bool:
        """
        Should we ask the user to clarify their intent?

        Returns True if confidence is too low.
        """
        return route.confidence < 0.4 and route.domain == Domain.GENERAL

    def get_clarification_message(self, query: str) -> str:
        """
        Generate a clarification message for unclear queries.
        """
        return (
            f"I'm not quite sure what you're asking about. Could you clarify?\n\n"
            f"For example:\n"
            f"• If it's about NixOS: mention 'nixos', 'flake', or 'configuration'\n"
            f"• If it's about programming: mention the language or error\n"
            f"• If it's about DevOps: mention the tool (docker, kubernetes, etc.)\n"
            f"• If it's networking: mention what you're trying to configure\n\n"
            f"Or just tell me more about what you're trying to do!"
        )


# Example usage and testing
if __name__ == "__main__":
    router = QueryRouter()

    test_queries = [
        # NixOS queries
        "how do I install firefox on nixos?",
        "create a flake.nix for python development",
        "nixos-rebuild switch is failing",

        # Programming queries
        "debug this python error",
        "how to write async javascript",
        "rust ownership rules explained",

        # DevOps queries
        "setup docker container",
        "kubernetes deployment yaml",
        "ci/cd pipeline with gitlab",

        # Networking queries
        "configure vpn on router",
        "port forwarding rules",
        "dns not resolving",

        # Database queries
        "postgresql query optimization",
        "mongodb schema design",
        "database migration strategy",

        # Security queries
        "ssl certificate setup",
        "firewall rules for web server",
        "secure ssh configuration",

        # Unclear queries
        "help me",
        "what should I do?",
        "computer is slow"
    ]

    print("🔀 Query Router Test\n")
    for query in test_queries:
        result = router.route(query)
        emoji = router.get_domain_emoji(result.domain)
        display_name = router.get_domain_display_name(result.domain)

        print(f"{emoji} {display_name}")
        print(f"   Query: {query}")
        print(f"   Domain: {result.domain.value}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Model: {result.specialist_model}")
        if result.should_offer_nixos_context:
            print(f"   💡 Could offer NixOS-specific solution!")
        print()
