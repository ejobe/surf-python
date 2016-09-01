#ifndef OCPCI_LIB_H
#define OCPCI_LIB_H

#include <stdint.h>
#include <stdlib.h>
#include <sys/types.h>
#include <stdbool.h>
#include <string.h>

#define OCPCI_SUCCESS 0
#define OCPCI_ERR_INVALID_HANDLE -1
#define OCPCI_ERR_OPEN -2
#define OCPCI_ERR_INVALID_REGISTER -3
#define OCPCI_ERR_MEM -4
#define OCPCI_ERR_UNALIGNED_WRITE -5

#define PCI_CONFIGURATION_SIZE 256

typedef struct ocpci_image_regs_t {
  uint32_t IMG_CTRL;
  uint32_t BA;
  uint32_t AM;
  uint32_t TA;
} ocpci_image_regs_t;

typedef struct ocpci_bridge_regs_t {
  uint8_t configuration[PCI_CONFIGURATION_SIZE];
  ocpci_image_regs_t P_Image[5];
  uint32_t P_ERR_CS;
  uint32_t P_ERR_ADDR;
  uint32_t P_ERR_DATA;
  // 16C-17F are unused (20 bytes)
  uint8_t gap0[20];
  ocpci_image_regs_t W_Image[5];
  uint32_t W_ERR_CS;
  uint32_t W_ERR_ADDR;
  uint32_t W_ERR_DATA;
  uint32_t CNF_ADDR;
  uint32_t CNF_DATA;
  uint32_t INT_ACK;
  uint32_t ICR;
  uint32_t ISR;
} ocpci_bridge_regs_t;

/** \brief The OCPCI device internal structure.
 *
 * Note that the structure name is "struct ocpci_dev_t"
 * but the typedef is "ocpci_dev_h" - the 'h' indicates
 * that it's a handle, and should not be accessed directly
 * but by using accessor functions.
 */
typedef struct ocpci_dev_t {
  bool valid;
  size_t wb_size;
  int cfg_fd;
  int bar0_fd;
  int bar1_fd;

  void *bar0;
  void *bar1;
  ocpci_bridge_regs_t *bridge;
} ocpci_dev_h;

int ocpci_lib_open(ocpci_dev_h *dev,
		   const char *path,
		   size_t wb_size);
void ocpci_lib_close(ocpci_dev_h *dev);

bool ocpci_is_open(ocpci_dev_h *dev);

ocpci_bridge_regs_t *ocpci_lib_get_bridge_regs(ocpci_dev_h *dev);
void *ocpci_lib_get_bar1(ocpci_dev_h *dev);

unsigned int ocpci_lib_bar0_read(ocpci_dev_h *dev, uint32_t offset);
int ocpci_lib_bar0_write(ocpci_dev_h *dev, uint32_t offset, unsigned int value);
unsigned int ocpci_lib_bar1_read(ocpci_dev_h *dev, uint32_t offset);
int ocpci_lib_bar1_write(ocpci_dev_h *dev, uint32_t offset, unsigned int value);

#endif
