from Py4GWCoreLib import Profession, Range, Routines, BuildMgr
from Py4GWCoreLib.Skill import Skill
from Py4GWCoreLib.Builds.Any.HeroAI import HeroAI as HeroAIBuild
from Py4GWCoreLib.Builds.Skills import SkillsTemplate


Air_of_Superiority_ID = Skill.GetID("Air_of_Superiority")
Panic_ID = Skill.GetID("Panic")
Mistrust_ID = Skill.GetID("Mistrust")
Ebon_Vanguard_Assassin_Support_ID = Skill.GetID("Ebon_Vanguard_Assassin_Support")
Cry_of_Pain_ID = Skill.GetID("Cry_of_Pain")
Unnatural_Signet_ID = Skill.GetID("Unnatural_Signet")
Cry_of_Frustration_ID = Skill.GetID("Cry_of_Frustration")
Overload_ID = Skill.GetID("Overload")
Power_Drain_ID = Skill.GetID("Power_Drain")
Shatter_Hex_ID = Skill.GetID("Shatter_Hex")
Flesh_of_My_Flesh_ID = Skill.GetID("Flesh_of_My_Flesh")
Breath_of_the_Great_Dwarf_ID = Skill.GetID("Breath_of_the_Great_Dwarf")
Ebon_Battle_Standard_of_Wisdom_ID = Skill.GetID("Ebon_Battle_Standard_of_Wisdom")


class Panic(BuildMgr):
    def __init__(self, match_only: bool = False):
        super().__init__(
            name="Panic",
            required_primary=Profession.Mesmer,
            template_code="OQBDAswzQ2g0A4i7imO4UDB5AA",
            required_skills=[
                Panic_ID,
                Ebon_Vanguard_Assassin_Support_ID,
                Cry_of_Frustration_ID,
            ],
            optional_skills=[
                Mistrust_ID,
                Cry_of_Pain_ID,
                Unnatural_Signet_ID,
                Power_Drain_ID,
                Shatter_Hex_ID,
                Ebon_Battle_Standard_of_Wisdom_ID,
                Overload_ID,
                Flesh_of_My_Flesh_ID,
                Breath_of_the_Great_Dwarf_ID,
            ],
        )
        if match_only:
            return

        self.SetFallback("HeroAI", HeroAIBuild(standalone_fallback=True))
        self.SetBlockedSkills([
            Air_of_Superiority_ID,
            Panic_ID,  # handled in local logic to allow for better fallback behavior
            Mistrust_ID,
            Ebon_Vanguard_Assassin_Support_ID,
            Cry_of_Pain_ID,
            Unnatural_Signet_ID,
            Cry_of_Frustration_ID,
            Overload_ID,
            Power_Drain_ID,
            Shatter_Hex_ID,
        ])
        self.SetSkillCastingFn(self._run_local_skill_logic)
        self.skills: SkillsTemplate = SkillsTemplate(self)

    def _run_local_skill_logic(self):
        if not Routines.Checks.Skills.CanCast():
            yield from Routines.Yield.wait(100)
            return False

        if Routines.Checks.Agents.InAggro() and (yield from self.skills.Any.PvE.Air_of_Superiority()):
            return True

        if (yield from self.skills.Any.NoAttribute.Breath_of_the_Great_Dwarf()):
            return True

        if self.IsSkillEquipped(Flesh_of_My_Flesh_ID):
            dead_ally_id: int = Routines.Agents.GetDeadAlly(Range.Spellcast.value)
            if dead_ally_id and (yield from self.CastSkillIDAndRestoreTarget(
                skill_id=Flesh_of_My_Flesh_ID,
                target_agent_id=dead_ally_id,
                log=False,
                aftercast_delay=250,
            )):
                return True

        if not Routines.Checks.Agents.InAggro():
            return False

        if (yield from self.skills.Any.PvE.Ebon_Vanguard_Assassin_Support()):
            return True
                
        if (yield from self.skills.Mesmer.DominationMagic.Panic()):
            return True
        
        if (yield from self.skills.Mesmer.DominationMagic.Shatter_Hex()):
            return True
        
        if self.IsSkillEquipped(Ebon_Battle_Standard_of_Wisdom_ID) and (yield from self.skills.Any.NoAttribute.Ebon_Battle_Standard_of_Wisdom()):
            return True
        
        if (yield from self.skills.Mesmer.DominationMagic.Mistrust()):
            return True

        if (yield from self.skills.Mesmer.DominationMagic.Power_Drain()):
            return True

        if (yield from self.skills.Any.PvE.Cry_of_Pain(allow_hex_fallback=False)):
            return True

        if (yield from self.skills.Mesmer.DominationMagic.Cry_of_Frustration()):
            return True

        if (yield from self.skills.Mesmer.DominationMagic.Overload()):
            return True

        if (yield from self.skills.Mesmer.DominationMagic.Unnatural_Signet()):
            return True

        if (yield from self.skills.Any.PvE.Cry_of_Pain()):
            return True

        yield
