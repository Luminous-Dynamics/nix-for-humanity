

# **A Strategic Analysis of the Luminous Nix Hardware Expansion Initiative: A Cartography of Incarnation**

### **Executive Summary**

This report presents a comprehensive strategic analysis of the Luminous Nix hardware expansion initiative, evaluating the viability of porting a Nix-based operating system to three distinct hardware ecosystems: the Steam Deck (Handheld PC), the Framework Laptop (Modular & Open Hardware), and Linux Mobile devices (PinePhone & Librem 5). The analysis, conducted under the "Cartography of Incarnation" mandate, assesses market opportunity, technical feasibility, user experience challenges, and the competitive landscape for each platform to provide actionable, data-driven recommendations.

The key findings indicate that each target platform represents a fundamentally different strategic challenge requiring a unique approach. The **Steam Deck** offers the largest addressable market but presents the highest user experience (UX) barrier and faces the strongest incumbent competition from Valve's highly polished SteamOS. Success in this segment is contingent on achieving near-perfect feature parity and a frictionless user experience, a significant technical and product design challenge. The **Framework Laptop** represents a smaller, niche market composed of a highly technical and ideologically aligned user base. It offers the lowest barrier to entry and represents a strategic "beachhead" for building community, brand credibility, and developer mindshare. Finally, the **Linux Mobile** ecosystem is a nascent, high-risk, and resource-intensive frontier. The technical gap between desktop Linux and a functional mobile OS is a chasm, requiring foundational investment in a Hardware Abstraction Layer (HAL) and a robust security model. This is a long-term, speculative venture, not a simple porting effort.

The report recommends a phased expansion strategy. **Phase 1** should prioritize the Framework Laptop as an entry point to establish a strong community and technical foundation. The **Phase 2** target should be the Steam Deck, a high-potential market that can only be addressed after solving critical UX challenges identified in this analysis. **Phase 3** should treat Linux Mobile as a long-term research and development initiative, focusing on foundational architectural development rather than an immediate product release. A unified approach to hardware abstraction is recommended to streamline all current and future platform enablement efforts.

---

## **Section 1: The NixOS Paradigm as a Strategic Differentiator**

### **1.1 Core Tenets of NixOS as a Multi-Device Foundation**

The strategic foundation of the Luminous Nix initiative rests on the unique architectural principles of the NixOS operating system: declarative configuration, reproducibility, and atomic upgrades. Unlike traditional, imperative operating systems where state is modified through a series of commands, a NixOS system is defined entirely by a central configuration file. This paradigm offers a powerful strategic advantage in a multi-device context, as it allows for a consistent, reliable, and user-defined software environment across disparate hardware form factors.1

This approach elevates a user's system configuration beyond a mere set of instructions into a portable, version-controlled blueprint for their entire computing experience. A user could, in theory, maintain a single, modular configuration that deploys their preferred tools, applications, and environment to their handheld gaming PC, their modular laptop, and their mobile device. This concept of a single source of truth for system configuration is a powerful narrative for technical users who value control and predictability. It transforms the configuration file into a form of digital identity—the portable soul of their computing life that transcends any single piece of hardware. This is a unique selling proposition in a fragmented hardware market and a core differentiator that Luminous Nix must leverage in its product positioning.

### **1.2 Strengths and Weaknesses in a Consumer Context**

The primary strength of the NixOS paradigm, as echoed by its community, is its potential to be the "endgame of distrohopping".1 For power users, the promise of achieving a perfectly stable, reproducible system that eliminates the constant churn and potential for breakage inherent in other Linux distributions is a powerful draw. This reliability is a key differentiator against traditional, mutable operating systems where software updates can introduce instability or unforeseen changes.

However, the paradigm's greatest weakness is its steep learning curve and the friction involved in making system changes. The fundamental workflow requires users to edit a configuration file and then "rebuild" the system to apply changes. This process is a significant UX hurdle, especially on devices that lack a physical keyboard, such as the Steam Deck.1 This friction is a critical barrier to mainstream adoption. Community sentiment captures this dichotomy perfectly; while many users declare that "NixOS ruined Linux for me" in a positive sense, others find it to be a "pain in the ass as any Nix environment" to maintain.1 The query from a self-described "lazy computer user" asking how much they will "hate it" encapsulates the strategic challenge: bridging the gap between the immense power offered to experts and the high barrier to entry for everyone else.1

---

## **Section 2: The Handheld PC Market: The Steam Deck Incarnation**

### **2.1 Market Opportunity Analysis**

The handheld PC gaming market presents the largest and most validated opportunity for the Luminous Nix initiative. The market is overwhelmingly dominated by Valve's Steam Deck, which sold an estimated 1.62 million units in its launch year of 2022 and reached a cumulative total of approximately 4 million units by early 2025\.2 In 2022, the Steam Deck accounted for virtually 100% of the measured market. Even with the entry of competitors like the Asus ROG Ally and Lenovo Legion Go, it maintained a commanding share of over 50% in 2023 and 48% in 2024\.3 The total market size across these major players reached 6 million units by the end of 2024, indicating a healthy and growing segment.2 Targeting the Steam Deck means targeting the cornerstone of this entire device category.

### **2.2 Technical & UX Assessment of NixOS on Steam Deck**

It is technically feasible to install and run NixOS on the Steam Deck, with community projects like Jovian NixOS facilitating the process.1 Users report that for the core gaming use case, the experience is "almost identical" to the default SteamOS, with comparable game compatibility.1 However, this technical feasibility is undermined by significant regressions in user experience.

The most critical friction points include:

* **Loss of UI Integration:** The seamless, console-like experience of the default SteamOS is broken. OS updates and even basic settings like timezone can no longer be managed through the simple Steam UI and must be handled via NixOS's configuration file.1 This is a major step backward in usability for the device's target audience.  
* **Ecosystem Fragmentation:** The rich modding ecosystem built around SteamOS is disrupted. Tools like Decky Loader require a more complex, declarative installation method, and specific plugins may not function at all unless they are properly packaged for the NixOS environment.1 While community workarounds sometimes exist, they add another layer of complexity for the user.1  
* **The "Keyboardless Rebuild" Problem:** The fundamental NixOS workflow of editing a text file and running a command-line tool to rebuild the system is profoundly ill-suited for a handheld gaming device. This process is described by users as something that "sucks on a device with no keyboard" and represents the single greatest UX challenge to overcome.1

This "usability chasm" effectively splits the potential market into two tiers. There is a small, highly technical tier of users who are already proficient with NixOS and are willing to tolerate these significant UX trade-offs to gain the benefits of reproducibility. Then there is the massive, mainstream tier of gamers, for whom such an experience would be unacceptable. To capture any meaningful market share, Luminous Nix cannot simply be a port of NixOS; it must include a user-friendly management layer that restores the lost "console-like" experience.

An alternative, lower-friction strategy exists in the form of installing only the Nix package manager onto the standard, immutable SteamOS.5 This allows users to supplement the base system with powerful tools from the

nixpkgs repository, such as compilers like gcc, without undertaking the high-risk endeavor of replacing the entire operating system.5 This approach serves as a strategic beachhead, introducing the power of Nix to the Steam Deck user base with minimal friction and acting as a potential gateway to a full Luminous Nix OS installation in the future.

### **2.3 Competitive OS Landscape**

* **Incumbent: SteamOS:** Developed by Valve, SteamOS is a highly polished, Arch-based immutable operating system tailored specifically for the Steam Deck.6 Its primary strategic advantage is its deep, seamless integration with the hardware, the Steam store, and its "Gaming Mode" UI, which provides a simple, console-like experience. It is a streamlined, tightly controlled ecosystem that benefits from Valve's official support, long-term engineering, and a centralized shader pre-caching network that improves game performance.6 Its main weakness is its locked-down nature, which frustrates power users who wish to customize their system or easily use non-Steam software.6  
* **Emerging Competitor: Bazzite:** Bazzite is a Fedora-based immutable OS from the Universal Blue project, explicitly designed as a more flexible and powerful alternative to SteamOS.6 It directly supports a wider range of hardware, including devices from Asus and Lenovo, and offers official support for NVIDIA GPUs.6 Its key advantages over SteamOS are its support for layering additional system packages via  
  rpm-ostree, Secure Boot compatibility for easier dual-booting with Windows, and out-of-the-box integration of non-Steam launchers like Lutris and Heroic.6 Bazzite proves there is an appetite for a more capable alternative to SteamOS, but it also means Luminous Nix would be entering a competitive field, not an empty one.  
* **Cautionary Tale: HoloISO & SteamFork:** These now-discontinued projects attempted to repackage Valve's SteamOS for general PC hardware.7 Their failure highlights the immense difficulty of maintaining a derivative OS and underscores a community sentiment that hardware vendors, not volunteers, should be funding such complex integration work.7 This serves as a crucial lesson for Luminous Nix regarding the resources required for long-term sustainability.

### **2.4 Strategic Assessment**

Targeting the Steam Deck offers access to the largest potential user base but requires overcoming the formidable UX and integration advantages of the incumbent, SteamOS. A Luminous Nix offering cannot be merely functional; it must be *as easy or easier* to use for the core gaming and system management tasks. The existence of Bazzite demonstrates a market for a more powerful alternative, but it also sets a high bar for features and hardware support. Luminous Nix must differentiate itself from Bazzite not just on features, but on the unique strengths of the core Nix paradigm—perfect reproducibility and declarative control—while simultaneously solving the critical usability challenges of that same paradigm on a handheld device.

---

## **Section 3: The Modular & Open Hardware Market: The Framework Laptop Incarnation**

### **3.1 Market Opportunity Analysis**

The Framework Laptop ecosystem represents a smaller, more concentrated market opportunity. While Framework does not release precise sales figures, community reports and statements at industry events in late 2024 suggest the company has sold a quantity in the "6 figures," ranging from 100,000 to 999,999 units.8 Although this constitutes a small fraction of the global laptop market, estimated at around 0.06%, it represents a uniquely valuable community of tech enthusiasts, developers, Linux power users, and advocates for the right-to-repair movement.8 This user base is not just tolerant of Linux; it is actively courted. Framework explicitly designs its laptops to be excellent Linux machines, provides pre-release hardware to distribution maintainers to ensure compatibility, and offers official support for distributions like Fedora and Ubuntu.10 This signifies a highly receptive, knowledgeable, and ideologically aligned target audience.

### **3.2 Technical & UX Assessment of NixOS on Framework**

The technical maturity of NixOS on the Framework Laptop is exceptionally high, presenting a low-friction user experience. The installation process is well-documented and follows a standard procedure for a Linux distribution.12 With modern Linux kernels, which are trivial to enable within a NixOS configuration (

boot.kernelPackages \= pkgs.linuxPackages\_latest;), hardware support is excellent, including for critical components like the Intel Wi-Fi card.13 Support for other hardware, such as the fingerprint reader, is enabled with a single configuration flag (

services.fprintd.enable \= true;).13 The process is so straightforward that one community guide concludes with the remark, "Seriously. That's it," indicating a high degree of success and minimal troubleshooting required.13 This smooth experience is bolstered by detailed community guides and active participation from the Framework team in support forums, further lowering the barrier to entry for interested users.12

### **3.3 Competitive OS Landscape**

Within the Framework community, Luminous Nix would face established and well-regarded competitors.

* **Officially Supported:** Fedora and Ubuntu LTS are the distributions with official support from Framework.10 Fedora is known for its aggressive kernel and software updates, appealing to users who want the latest features, while Ubuntu LTS offers a more conservative and stable experience.10  
* **Community Favorites:** For users transitioning from other operating systems, Linux Mint is highly recommended due to its familiar Windows-like Cinnamon desktop environment.14 Zorin OS is similarly positioned as a user-friendly alternative for those accustomed to Windows.14

Luminous Nix would not, and should not, attempt to compete with Mint or Zorin on the metric of "ease of use for beginners." Instead, its strategic position is to appeal to the advanced user who has already selected a Framework Laptop precisely for its principles of user control, customization, and transparency. These are the same principles that define the core value proposition of NixOS. This creates a powerful ideological symbiosis. Framework applies the principles of modularity and open source to hardware, releasing CAD templates and open source firmware.11 NixOS applies these same principles to software, where the entire system is defined in a version-controllable source file. For a user who buys a Framework laptop, a Luminous Nix OS is not just another alternative; it is the obvious, philosophically-aligned software conclusion to their hardware choice.

### **3.4 Strategic Assessment**

The Framework Laptop represents the path of least resistance and greatest strategic alignment for the Luminous Nix initiative. The market is self-selecting for users who are predisposed to value the deep, granular control that NixOS provides. This platform is an ideal "beachhead" for Luminous Nix. Achieving success here, by creating the definitive NixOS experience for Framework hardware, would generate powerful, positive word-of-mouth within an influential community of Linux power users, developers, and tech content creators. This would build invaluable brand credibility and technical expertise that could then be leveraged for subsequent pushes into more challenging and mainstream markets.

---

## **Section 4: The Linux Mobile Frontier: The PinePhone & Librem 5 Incarnations**

### **4.1 Market Opportunity Analysis**

The Linux mobile market is a micro-niche, driven almost exclusively by open-source developers, privacy absolutists, and hobbyists. Precise sales figures are not public, but available data points to a very small user base. A 2022 poll of PinePhone owners garnered approximately 3,000 responses, which was estimated to represent less than 5% of all owners, suggesting a total community size in the tens of thousands.15 Purism, the company behind the Librem 5, reported total revenue across all its products of approximately $9 million in 2023, indicating that its phone is a small part of a niche company's portfolio.16 The value proposition for these devices is not performance, app compatibility, or user experience, but rather user control, privacy, and the ability to run a mainline Linux kernel.17 The target user is a developer willing to tolerate significant flaws, not a mainstream consumer.

### **4.2 Technical & UX Assessment of Mobile NixOS**

The state of NixOS on mobile hardware is experimental and fraught with challenges.

* **PinePhone:** Mobile NixOS has official support for the PinePhone, with a detailed wiki page documenting feature status.19 While core functions like basic calling, SMS, mobile data, and GPS are reported to be working, the list of broken or unsupported features is extensive and critical.19 MMS, wake-on-WiFi, reliable alarms, hardware video acceleration, and camera autofocus are all non-functional.19 A user who daily-drove a PinePhone for three years described it as a "largely painful experience" with "many broken or half-broken features" and "very slow" software progress.21  
* **Librem 5:** There is no official Mobile NixOS support for the Librem 5\.22 Community members have managed to boot the OS, but with major hardware components like the camera and sound during phone calls being completely non-functional.22 Getting the system to work at all requires using Purism's device-specific kernel source, as the upstream Linux kernel is insufficient, highlighting deep, non-standard hardware dependencies that must be individually addressed.23

### **4.3 The Abstraction Imperative: Lessons from Android**

The persistent, feature-by-feature struggle of Mobile NixOS and its contemporaries is a direct symptom of a fundamental architectural gap. A modern mobile operating system requires a robust abstraction layer to manage the immense complexity of mobile-specific hardware (e.g., modems, sensors, power management ICs).

* **The Hardware Abstraction Layer (HAL):** Android's architecture successfully solves this problem by defining a standardized HAL with interfaces (AIDL) that hardware vendors must implement.24 This decouples the development of the high-level Android OS from the low-level, often proprietary, driver implementations for specific hardware. The endless game of "whack-a-mole" with hardware quirks on Linux mobile is a direct result of the  
  *absence* of such a mature, comprehensive HAL.  
* **The Application Sandbox:** Mature mobile operating systems also enforce security and stability through strong, kernel-level sandboxing. Android assigns a unique user ID (UID) to each app and runs it in an isolated process, preventing apps from interfering with each other or the core system.26 Google's Fuchsia OS follows a similar principle, isolating all drivers and system components in user space to enforce least privilege.27 A viable Linux mobile OS must implement a similarly robust security model to be trusted by users.

This "HAL Chasm" defines the core strategic challenge for Luminous Nix in the mobile space. The problem is not merely about packaging mobile user interfaces or fixing individual driver bugs; it is about bridging the immense architectural gap between a desktop Linux distribution and a functional, secure mobile OS. Without a strategic, long-term commitment to building a HAL-equivalent framework, any effort in this space will be an endless and unwinnable maintenance burden.

### **4.4 Competitive OS Landscape**

* **Linux Native:** The direct competitors are other mobile Linux projects like postmarketOS (based on Alpine Linux), Ubuntu Touch, and Manjaro ARM.17 These projects face the exact same fundamental hardware support challenges, leading to a user experience where "mileage is going to vary big time" depending on the OS and hardware combination.21 Among these, postmarketOS is often praised for its user-friendly Phosh interface and excellent documentation.17  
* **Privacy-Hardened Android:** For the target user prioritizing privacy and security, GrapheneOS and CalyxOS are far more mature and practical alternatives.29 By building on top of the Android Open Source Project (AOSP), they leverage the mature Android HAL and driver ecosystem, ensuring full hardware functionality on supported devices (Google Pixels). They then replace the upper layers with a de-Googled, security-hardened system. GrapheneOS, with its innovative approach to sandboxed Google Play Services, offers vastly superior app compatibility and a more robust security model than any current Linux mobile offering.29 They represent a much more viable choice for a daily-use private phone today.

### **4.5 Strategic Assessment**

The Linux Mobile market is currently a "developer's market," not a consumer market. A successful entry into this space is not a porting project; it is a multi-year, foundational research and development effort to build a mobile-first OS architecture. This includes creating a comprehensive hardware abstraction layer and a robust, modern security model. The resource investment required to even reach feature parity with other Linux mobile projects is high, and the investment needed to approach the stability and security of GrapheneOS is astronomical. This endeavor should be framed as a long-term, high-risk, potentially high-reward venture into defining the future of open computing, not as a short-term product strategy.

---

## **Section 5: Strategic Synthesis & Actionable Recommendations**

### **5.1 Comparative Platform Analysis**

The analysis of the three target hardware platforms reveals distinct profiles of opportunity, risk, and required investment. The following table synthesizes these findings to provide a clear, at-a-glance comparison for strategic decision-making. It distills the complex analysis of the preceding sections into a direct comparison of risk versus reward, justifying a phased and focused rollout strategy.

| Platform | Estimated Addressable Market (Units) | Primary User Persona | NixOS Technical Maturity Score (1-10) | Key Competitive Threats | Resource Investment Level | Strategic Priority Recommendation |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Steam Deck** | \~4 Million | Mainstream Gamer | 4 | SteamOS, Bazzite | High | Phase 2 |
| **Framework Laptop** | \~100k \- 999k | Linux Power User/Developer | 9 | Fedora, Ubuntu | Low | Phase 1 |
| **Linux Mobile** | \~10k \- 50k | Privacy Advocate/Hobbyist | 2 | postmarketOS, GrapheneOS | Very High | Phase 3 (R\&D) |

### **5.2 A Unified "Incarnation" Framework for Hardware Abstraction**

To avoid the pitfalls of ad-hoc, platform-specific porting efforts, Luminous Nix should initiate a long-term project to create a unified hardware enablement framework. This initiative, inspired by the proven architectural principles of the Android HAL 25 and Fuchsia's user-space driver model 27, would represent a significant strategic investment in future scalability. The framework's goal would be to define stable, declarative interfaces for common hardware classes (e.g., modems, cameras, power management, sensors). This would allow the core Luminous Nix OS to remain clean and hardware-agnostic, while device-specific support could be developed as modular, isolated components. Such an investment would dramatically lower the cost and complexity of supporting future hardware platforms beyond the three analyzed in this report.

### **5.3 Sustainable Go-to-Market Models**

To ensure long-term viability, Luminous Nix must adopt a sustainable business model that moves beyond a purely volunteer-driven community project. Several proven models are applicable:

* **Professional Services & Enterprise Support:** Following the successful Red Hat model, Luminous Nix can offer paid support contracts, consulting, and custom engineering services for enterprises wishing to deploy the OS across fleets of devices, such as company-issued Framework laptops or specialized handhelds.31  
* **SaaS/Management Plane:** A compelling opportunity exists to offer a cloud-based service for managing fleets of Luminous Nix devices. The declarative and reproducible nature of NixOS is uniquely suited for centralized, version-controlled configuration management at scale.  
* **Open Core Model:** The core Luminous Nix OS can remain fully open source, while proprietary add-ons are sold. These could include a graphical, user-friendly "Configuration Studio" to lower the barrier to entry for less technical users, or certified enterprise security and compliance modules.31  
* **Pay-What-You-Want (PWYW) / Donations:** For community-focused editions, a PWYW model can be effective. Case studies on PWYW pricing show that success depends on managing user psychology. It is crucial to suggest a recommended price and clearly articulate the value of contributions to the project's health, as this helps users overcome the self-image concern of appearing "cheap," which can otherwise lead them to not contribute at all.33

### **5.4 Prioritized Expansion Roadmap**

A disciplined, phased approach offers the highest probability of sustainable success.

* **Phase 1 (0-12 Months): The Beachhead \- Framework Laptop.**  
  * **Objective:** Focus all initial engineering and community efforts on creating the definitive, best-in-class NixOS experience for the Framework Laptop.  
  * **Actions:** Engage directly with the Framework community, become a primary contributor to the nixos-hardware project, and produce high-quality documentation and installation guides.  
  * **Goal:** Establish Luminous Nix as a credible, respected, and technically excellent player within an influential community, building the brand capital and expertise needed for future expansion.  
* **Phase 2 (12-24 Months): The Mainstream Push \- Steam Deck.**  
  * **Objective:** Leverage the credibility and technical foundation from Phase 1 to address the larger Steam Deck market.  
  * **Actions:** The primary focus must be on solving the UX challenges. This requires developing a graphical overlay or dedicated application that simplifies system updates, mod management (e.g., Decky Loader integration), and basic configuration changes without forcing users into a command-line workflow. Concurrently, promote the "Nix package manager on SteamOS" installation as a low-friction entry point to the ecosystem.5  
  * **Goal:** Capture a meaningful share of the power-user segment of the Steam Deck market while creating a viable path for less technical users to adopt the full OS.  
* **Phase 3 (24+ Months): The R\&D Frontier \- Mobile.**  
  * **Objective:** Treat the mobile space as a long-term research and development project, not a short-term product launch.  
  * **Actions:** Begin foundational work on the "Unified Incarnation Framework" for hardware abstraction (see 5.2). Focus on solving the core architectural problems of creating a mobile HAL and a robust security model. Do not commit to a product release timeline.  
  * **Goal:** Position Luminous Nix to be a leader in the *next* generation of open, user-controlled computing devices, rather than fighting a resource-intensive and likely losing battle in the current generation.

### **5.5 Concluding Analysis**

The Luminous Nix Hardware Expansion Strategy is an ambitious initiative that intersects with three vastly different markets, each with its own unique user base, technical challenges, and competitive dynamics. A monolithic, "one size fits all" porting approach is destined for failure.

Success hinges on a nuanced strategic recognition of each hardware "incarnation." By first prioritizing the ideologically aligned and technically receptive Framework Laptop community, Luminous Nix can build the foundational brand capital and engineering expertise required to subsequently tackle the larger but more challenging Steam Deck market. The mobile frontier, in its current state, should be viewed not as a market to be captured, but as a frontier to be explored—a speculative, long-term investment in the company's future technological sovereignty. A disciplined, phased, and architecturally-minded approach offers the most promising path to sustainable success.

#### **Works cited**

1. Has anyone installed NixOS (not Nix) on a Steam Deck? How did ..., accessed August 20, 2025, [https://www.reddit.com/r/NixOS/comments/1irol0w/has\_anyone\_installed\_nixos\_not\_nix\_on\_a\_steam/](https://www.reddit.com/r/NixOS/comments/1irol0w/has_anyone_installed_nixos_not_nix_on_a_steam/)  
2. Analysts: Over three years, Valve has sold around 4 million Steam Decks, capturing the portable PC market | WN Hub, accessed August 20, 2025, [https://wnhub.io/news/analytics/item-47202](https://wnhub.io/news/analytics/item-47202)  
3. Analysts: Over three years, Valve has sold around 4 million Steam Decks, capturing the portable PC market | App2top, accessed August 20, 2025, [https://app2top.com/news/analysts-over-three-years-valve-has-sold-around-4-million-steam-decks-capturing-the-portable-pc-market-278096.html](https://app2top.com/news/analysts-over-three-years-valve-has-sold-around-4-million-steam-decks-capturing-the-portable-pc-market-278096.html)  
4. The best Steam Deck alternatives in 2025: top picks to play on the go \- TechRadar, accessed August 20, 2025, [https://www.techradar.com/gaming/best-steam-deck-alternatives](https://www.techradar.com/gaming/best-steam-deck-alternatives)  
5. Using Nix packages in Steam Deck \- xpressrazor \- WordPress.com, accessed August 20, 2025, [https://xpressrazor.wordpress.com/2024/01/11/using-nix-packages-in-steam-deck/](https://xpressrazor.wordpress.com/2024/01/11/using-nix-packages-in-steam-deck/)  
6. Bazzite vs SteamOS \- Which one to choose? Key differences, accessed August 20, 2025, [https://theserverhost.com/blog/post/bazzite-vs-steamos](https://theserverhost.com/blog/post/bazzite-vs-steamos)  
7. Bazzite isn't SteamOS (and that's ok\!) | bret.io, accessed August 20, 2025, [https://bret.io/blog/2025/bazzite-isnt-steamos/](https://bret.io/blog/2025/bazzite-isnt-steamos/)  
8. How many laptops have FW sold? \- General Topics \- Framework Community, accessed August 20, 2025, [https://community.frame.work/t/how-many-laptops-have-fw-sold/60649](https://community.frame.work/t/how-many-laptops-have-fw-sold/60649)  
9. How many devices per batch? \- Framework Laptop 12, accessed August 20, 2025, [https://community.frame.work/t/how-many-devices-per-batch/68213](https://community.frame.work/t/how-many-devices-per-batch/68213)  
10. Linux Compatibility on the Framework Laptop, accessed August 20, 2025, [https://frame.work/linux](https://frame.work/linux)  
11. System76 and Framework \- Spiral Array, accessed August 20, 2025, [https://www.spiralarray.com/blog/2024/02/05/System76\_and\_Framework.html](https://www.spiralarray.com/blog/2024/02/05/System76_and_Framework.html)  
12. NixOS on the Framework Laptop 13 \- Framework Guides, accessed August 20, 2025, [https://guides.frame.work/Guide/NixOS+on+the+Framework+Laptop+13/400](https://guides.frame.work/Guide/NixOS+on+the+Framework+Laptop+13/400)  
13. Graham Christensen: NixOS on the Framework, accessed August 20, 2025, [https://grahamc.com/](https://grahamc.com/)  
14. The best Linux distros for beginners in 2025 make switching from MacOS or Windows so easy | ZDNET, accessed August 20, 2025, [https://www.zdnet.com/article/the-best-linux-distros-for-beginners-in-2025-make-switching-from-macos-or-windows-easy/](https://www.zdnet.com/article/the-best-linux-distros-for-beginners-in-2025-make-switching-from-macos-or-windows-easy/)  
15. PinePhone community poll results \- PINE64, accessed August 20, 2025, [https://pine64.org/2022/01/31/pinephone-community-poll-results/](https://pine64.org/2022/01/31/pinephone-community-poll-results/)  
16. 2023 Finance Report: Profitable, More Assets than Liabilities, Over $9m in Sales, 50% Margin \- Purism, accessed August 20, 2025, [https://puri.sm/posts/2023-finance-report-profitable-more-assets-than-liabilities-over-9m-in-sales-50-margin/](https://puri.sm/posts/2023-finance-report-profitable-more-assets-than-liabilities-over-9m-in-sales-50-margin/)  
17. Trying Out the PinePhone in 2023 | Welcome to The Privacy Dad's Blog\!, accessed August 20, 2025, [https://theprivacydad.com/trying-pinephone-in-2023/](https://theprivacydad.com/trying-pinephone-in-2023/)  
18. postmarketOS // real Linux distribution for phones, accessed August 20, 2025, [https://postmarketos.org/](https://postmarketos.org/)  
19. PinePhone \- NixOS Wiki, accessed August 20, 2025, [https://nixos.wiki/wiki/PinePhone](https://nixos.wiki/wiki/PinePhone)  
20. Pine64 PinePhone \- Mobile NixOS, accessed August 20, 2025, [https://mobile.nixos.org/devices/pine64-pinephone.html](https://mobile.nixos.org/devices/pine64-pinephone.html)  
21. State of it.Linux Phone? \- ARM \- Manjaro Linux Forum, accessed August 20, 2025, [https://forum.manjaro.org/t/state-of-it-linux-phone/173731](https://forum.manjaro.org/t/state-of-it-linux-phone/173731)  
22. Mobile NixOS on Librem 5 \- Software \- Purism community, accessed August 20, 2025, [https://forums.puri.sm/t/mobile-nixos-on-librem-5/28586](https://forums.puri.sm/t/mobile-nixos-on-librem-5/28586)  
23. Can someone with serial console access try NixOS kernel on Librem 5? \- \#20 by ookhoi, accessed August 20, 2025, [https://forums.puri.sm/t/can-someone-with-serial-console-access-try-nixos-kernel-on-librem-5/19121/20](https://forums.puri.sm/t/can-someone-with-serial-console-access-try-nixos-kernel-on-librem-5/19121/20)  
24. What is a Hardware Abstraction Layer and How Does it Work? \- Lenovo, accessed August 20, 2025, [https://www.lenovo.com/us/en/glossary/hardware-abstraction-layer/](https://www.lenovo.com/us/en/glossary/hardware-abstraction-layer/)  
25. Hardware abstraction layer (HAL) overview | Android Open Source ..., accessed August 20, 2025, [https://source.android.com/docs/core/architecture/hal](https://source.android.com/docs/core/architecture/hal)  
26. Application Sandbox | Android Open Source Project, accessed August 20, 2025, [https://source.android.com/docs/security/app-sandbox](https://source.android.com/docs/security/app-sandbox)  
27. Fuchsia architecture, accessed August 20, 2025, [https://fuchsia.dev/fuchsia-src/get-started/learn/intro/architecture](https://fuchsia.dev/fuchsia-src/get-started/learn/intro/architecture)  
28. PineTab: Operating systems \- PINE64, accessed August 20, 2025, [https://pine64.org/documentation/PineTab/Operating\_systems/](https://pine64.org/documentation/PineTab/Operating_systems/)  
29. How does CalyxOS compare to GrapheneOS? \- Hacker News, accessed August 20, 2025, [https://news.ycombinator.com/item?id=28091157](https://news.ycombinator.com/item?id=28091157)  
30. Compare GrapheneOS vs. Ubuntu Touch in 2025 \- Slashdot, accessed August 20, 2025, [https://slashdot.org/software/comparison/GrapheneOS-vs-Ubuntu-Touch/](https://slashdot.org/software/comparison/GrapheneOS-vs-Ubuntu-Touch/)  
31. Business models for open-source software \- Wikipedia, accessed August 20, 2025, [https://en.wikipedia.org/wiki/Business\_models\_for\_open-source\_software](https://en.wikipedia.org/wiki/Business_models_for_open-source_software)  
32. The challenge of building sustainable open-source business tools \- lessons from 3 months of solo development : r/opensource \- Reddit, accessed August 20, 2025, [https://www.reddit.com/r/opensource/comments/1maia2w/the\_challenge\_of\_building\_sustainable\_opensource/](https://www.reddit.com/r/opensource/comments/1maia2w/the_challenge_of_building_sustainable_opensource/)  
33. Pay-What-You-Want, Identity and Self-Signaling in Markets, accessed August 20, 2025, [https://marketing.wharton.upenn.edu/wp-content/uploads/2020/07/Pay-What-You-Want-PAPER-Gneezy-Ayelet-4-12-2012.pdf](https://marketing.wharton.upenn.edu/wp-content/uploads/2020/07/Pay-What-You-Want-PAPER-Gneezy-Ayelet-4-12-2012.pdf)  
34. \[Case Study\] How a Pay-What-You-Want Pricing Model Can Generate More Revenue, accessed August 20, 2025, [https://copyblogger.com/pay-what-you-want-pricing/](https://copyblogger.com/pay-what-you-want-pricing/)