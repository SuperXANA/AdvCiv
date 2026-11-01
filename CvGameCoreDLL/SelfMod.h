// advc.092b: Let's put all self-modifying code in a single place
#pragma once
#ifndef SELF_MOD_H
#define SELF_MOD_H

// Runtime modifications to the native code of Civ4BeyondSword.exe (v3.19)
class Civ4BeyondSwordPatches
{
public:
	void patchPlotIndicatorSize(); // (exposed to Python via CyGameCoreUtils) 
	bool isPlotIndicatorSizePatched() const { return m_bPlotIndicatorSizePatched; }
	// <advc.092c>
	void setHelpTextAreaSize(float fWidth); // (exposed to Python via CyGame)
	float getHelpTextAreaWidth() const { return m_fHelpTextAreaWidth; }
	bool isHelpTextAreaWidthPatched() const { return (getHelpTextAreaWidth() != 0); }
	// </advc.092c>
	// XANA: 10-27-2026 Solais a Tuath Strategy Entry "Sol Says" Patch
	void patchSidSays();
	void resetSidSaysDiscovery() { m_bSidSaysDiscoveryDone = false; }
	bool isSidSaysDiscoveryDone() const { return m_bSidSaysDiscoveryDone; }
	bool isSidSaysPatched() const { return m_bSidSaysPatched; }
	// XANA: 10-27-2026 Solais a Tuath Strategy Entry "Sol Says" Patch
	
	Civ4BeyondSwordPatches()
	:	m_bPlotIndicatorSizePatched(false), m_fHelpTextAreaWidth(0), m_bSidSaysPatched(false) // XANA: 10-27-2026 Solais a Tuath Strategy Entry "Sol Says" Patch
	, m_bSidSaysDiscoveryDone(false) // XANA: 10-31-2026 CvGame-controlled discovery state (ChatGPT)
	{}

private:
	bool m_bPlotIndicatorSizePatched;
	float m_fHelpTextAreaWidth; // advc.092c
	// XANA: 10-27-2026 Solais a Tuath Strategy Entry "Sol Says" Patch
	bool m_bSidSaysPatched;
	bool m_bSidSaysDiscoveryDone; // XANA: 10-31-2026 CvGame-controlled discovery state (ChatGPT)
	// XANA: 10-27-2026 Solais a Tuath Strategy Entry "Sol Says" Patch
	void showErrorMsgToPlayer(CvWString szMsg);
};

namespace smc
{
	extern Civ4BeyondSwordPatches BtS_EXE;
}

#endif
