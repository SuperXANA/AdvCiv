class AlignmentScore
{
public:
    AlignmentScore(int baseHigh = 0, int baseLow = 0,
                   int highDecay = 0, int lowDecay = 0,
                   int maxDelta = MAX_INT,
                   bool independent = false)
    : m_iBaseHigh(baseHigh),
      m_iBaseLow(baseLow),
      m_iHighDecay(highDecay),
      m_iLowDecay(lowDecay),
      m_iMaxDelta(maxDelta),
      m_bAlignmentGoodEvilIsIndependent(independent),
      m_iPermHigh(0),
      m_iPermLow(0),
      m_iHead(0),
      m_iCount(0) {}
    void nextTurn();
    void changeAlignmentTowardsPositive(int iChange);
    void changeAlignmentTowardsNegative(int iChange);
    void changePermanentAlignmentTowardsPositive(int iChange);
    void changePermanentAlignmentTowardsNegative(int iChange);
    void decay();
    AlignmentValue get() const;
    void read(FDataStreamBase* pStream);
    void write(FDataStreamBase* pStream);
private:
    static const int m_iSampleSize = 10; // XANA (note): default value for speed, game code can't modify
    int index(int i) const { return (m_iHead - i + m_iSampleSize) % m_iSampleSize; }
    AlignmentValue m_buffer[m_iSampleSize];
    int m_iHead;
    int m_iCount;
    int m_iBaseHigh;
    int m_iBaseLow;
    int m_iPermHigh;
    int m_iPermLow;
    int m_iHighDecay;
    int m_iLowDecay;
    int m_iMaxDelta;
    bool m_bAlignmentGoodEvilIsIndependent;
};
